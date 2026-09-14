#!/usr/bin/env python3
from __future__ import annotations

import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
import tempfile
from pathlib import Path

import pymupdf

from .domus import parse_public_living_domus
from .domus_stream import living_domus_for_source, living_domus_from_emission
from .hashing import file_emission_from_bytes, TardiSHAError, validate_nonce
from .route import source_route_witness_from_emission



TAG_KEY = 'TardiSHAReturn'
TAG_VALUE = '/GrimChainSelfV3'
DEPTH_KEY = 'TardiSHADepth'
SEAL_KEY = 'TardiSHASealHex'
BASE_SIZE_KEY = 'TardiSHABaseSize'
NONCE_KEY = 'TardiSHANonce'

# PDF presentation is deterministic and separate from GrimChain mathematics.
# The exact Unicode seal remains the stored return witness; rendered pages use only
# the TardiSHA-owned runtime font body and never substitute arbitrary system fonts.

_RUNTIME_FONT_NAMES = (
    "NotoMusic-Regular.ttf",
    "NotoSans-Regular.ttf",
    "NotoSansBalinese-Regular.ttf",
    "NotoSansBrahmi-Regular.ttf",
    "NotoSansCuneiform-Regular.ttf",
    "NotoSansCypriot-Regular.ttf",
    "NotoSansElbasan-Regular.ttf",
    "NotoSansEthiopic-Regular.ttf",
    "NotoSansLydian-Regular.ttf",
    "NotoSansMath-Regular.ttf",
    "NotoSansNKo-Regular.ttf",
    "NotoSansRunic-Regular.ttf",
    "NotoSansSundanese-VariableFont_wght.ttf",
    "NotoSansSylotiNagri-Regular.ttf",
    "NotoSansSymbols-Regular.ttf",
    "NotoSansSymbols2-Regular.ttf",
    "NotoSansThaana-Regular.ttf",
    "NotoSansTifinagh-Regular.ttf",
    "NotoSerifTibetan-Regular.ttf",
)

RENDER_WIDTH_PX = 1600
PDF_FONT_SIZE_PT = 11.0
PDF_LINE_GAP_PT = 4.0
SIDE_PAD_PX = 40
PAGE_SIDE = 42.0


def _byte_difference(left: str, right: str) -> int:
    """Exact non-negative UTF-8 residual; zero iff the bodies are identical."""
    a = left.encode("utf-8")
    b = right.encode("utf-8")
    shared = min(len(a), len(b))
    return abs(len(a) - len(b)) + sum(a[i] != b[i] for i in range(shared))


def _runtime_font_directory() -> Path:
    """Return the complete TardiSHA-owned runtime font directory."""
    module_root = Path(__file__).resolve().parent.parent
    candidates = (
        Path("/usr/local/share/fonts/tardisha"),
        module_root / "fonts" / "runtime",
        Path("/usr/share/fonts/truetype/tardisha"),
        Path("/Library/Fonts"),
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts",
    )
    for directory in candidates:
        if all((directory / name).is_file() for name in _RUNTIME_FONT_NAMES):
            return directory
    raise RuntimeError("TardiSHA runtime fonts are not installed as one complete font body")


def _renderer_font_body() -> tuple[tuple[Path, frozenset[int]], ...]:
    """Load the canonical font coverage as invocation-local Vāhana."""
    directory = _runtime_font_directory()
    body: list[tuple[Path, frozenset[int]]] = []
    for name in _RUNTIME_FONT_NAMES:
        path = directory / name
        font = TTFont(path, fontNumber=0, lazy=True)
        try:
            cmap = frozenset((font.getBestCmap() or {}).keys())
        finally:
            font.close()
        body.append((path, cmap))
    return tuple(body)




def _render_png_pages(seal: str, page_width: float, page_height: float) -> tuple[bytes, ...]:
    """Render every exact GrimChain glyph with deterministic measured wrapping."""
    parse_public_living_domus(seal)
    if not seal:
        raise RuntimeError("Grimchain renderer received an empty seal")
    usable_width = page_width - 2 * PAGE_SIDE
    usable_height = page_height - 2 * PAGE_SIDE
    if usable_width <= 0 or usable_height <= 0:
        raise RuntimeError("PDF page has no usable Grimchain body area")

    # Vāhana: font coverage, loaded fonts, and measured widths live only for this render.
    # Raster size is derived from a normal 11-point PDF text size so the written
    # return has familiar reading scale on different page geometries.
    raster_scale = RENDER_WIDTH_PX / usable_width
    font_px = max(1, round(PDF_FONT_SIZE_PT * raster_scale))
    line_gap_px = max(1, round(PDF_LINE_GAP_PT * raster_scale))
    font_body = _renderer_font_body()
    pil_fonts: dict[Path, ImageFont.FreeTypeFont] = {}
    glyph_metrics: dict[tuple[Path, str], tuple[int, int, int]] = {}
    measure = Image.new("L", (8, 8), 255)
    measure_draw = ImageDraw.Draw(measure)
    items: list[tuple[str, ImageFont.FreeTypeFont, int, int, int]] = []

    for ch in seal:
        cp = ord(ch)
        path = next((path for path, cmap in font_body if cp in cmap), None)
        if path is None:
            raise RuntimeError(f"TardiSHA runtime font body does not render U+{cp:04X}")
        font = pil_fonts.get(path)
        if font is None:
            font = ImageFont.truetype(str(path), font_px)
            pil_fonts[path] = font
        key = (path, ch)
        metrics = glyph_metrics.get(key)
        if metrics is None:
            advance = max(1, round(measure_draw.textlength(ch, font=font)))
            box = measure_draw.textbbox((0, 0), ch, font=font, anchor="ls")
            metrics = (advance, box[1], box[3])
            glyph_metrics[key] = metrics
        advance, top, bottom = metrics
        items.append((ch, font, advance, top, bottom))

    max_width = RENDER_WIDTH_PX - 2 * SIDE_PAD_PX
    lines: list[tuple[list[tuple[str, ImageFont.FreeTypeFont, int, int, int]], int]] = []
    current: list[tuple[str, ImageFont.FreeTypeFont, int, int, int]] = []
    current_width = 0
    for item in items:
        if current and current_width + item[2] > max_width:
            lines.append((current, current_width))
            current = []
            current_width = 0
        current.append(item)
        current_width += item[2]
    if current:
        lines.append((current, current_width))

    normal_line_height = font_px + line_gap_px
    row_slot_height = 2 * normal_line_height
    canvas_height = max(1, round(RENDER_WIDTH_PX * usable_height / usable_width))
    lines_per_page = (canvas_height - 2 * SIDE_PAD_PX) // row_slot_height
    if lines_per_page < 1:
        raise RuntimeError("PDF page cannot contain one two-line Grimchain row at the configured font size")

    pages: list[bytes] = []
    for start in range(0, len(lines), lines_per_page):
        page_lines = lines[start:start + lines_per_page]
        image = Image.new("L", (RENDER_WIDTH_PX, canvas_height), 255)
        draw = ImageDraw.Draw(image)
        slot_top = SIDE_PAD_PX
        for line, line_width in page_lines:
            x = (RENDER_WIDTH_PX - line_width) // 2
            line_top = min(item[3] for item in line)
            line_bottom = max(item[4] for item in line)
            line_ink_height = max(1, line_bottom - line_top)
            baseline = slot_top + (row_slot_height - line_ink_height) // 2 - line_top
            for ch, font, advance, _top, _bottom in line:
                draw.text((x, baseline), ch, font=font, fill=0, anchor="ls")
                x += advance
            slot_top += row_slot_height
        output = BytesIO()
        image.save(output, format="PNG", optimize=False, compress_level=9)
        pages.append(output.getvalue())
    return tuple(pages)


def _append_text_pages(doc: pymupdf.Document, seal: str, page_width: float, page_height: float) -> tuple[int, ...]:
    """Append deterministic GrimChain render pages using only TardiSHA fonts."""
    pngs = _render_png_pages(seal, page_width, page_height)
    page_xrefs: list[int] = []
    for png in pngs:
        page = doc.new_page(width=page_width, height=page_height)
        rect = pymupdf.Rect(PAGE_SIDE, PAGE_SIDE, page_width - PAGE_SIDE, page_height - PAGE_SIDE)
        page.insert_image(rect, stream=png, keep_proportion=True)
        page_xrefs.append(page.xref)
    return tuple(page_xrefs)



def _save_incremental(doc: pymupdf.Document, path: Path) -> None:
    doc.subset_fonts()
    doc.save(
        path,
        incremental=True,
        no_new_id=True,
        encryption=pymupdf.PDF_ENCRYPT_KEEP,
        preserve_metadata=True,
    )


def _append_self_revision(pdf: Path, seal: str, depth: int, base_size: int, *, nonce: int) -> None:
    doc = pymupdf.open(pdf)
    try:
        last = doc[-1].rect
        page_xrefs = _append_text_pages(doc, seal, last.width, last.height)
        marker_xref = page_xrefs[0]
        doc.xref_set_key(marker_xref, TAG_KEY, TAG_VALUE)
        doc.xref_set_key(marker_xref, DEPTH_KEY, str(depth))
        doc.xref_set_key(marker_xref, SEAL_KEY, "<" + seal.encode("utf-8").hex().upper() + ">")
        doc.xref_set_key(marker_xref, BASE_SIZE_KEY, str(base_size))
        doc.xref_set_key(marker_xref, NONCE_KEY, str(validate_nonce(nonce)))
        _save_incremental(doc, pdf)
    finally:
        doc.close()


def _find_self_xrefs(doc: pymupdf.Document) -> tuple[tuple[int, int, str, int, int], ...]:
    """Return every explicit TardiSHA PDF return marker in physical xref order."""
    found: list[tuple[int, int, str, int, int]] = []
    for xref in range(1, doc.xref_length()):
        tag_type, tag_value = doc.xref_get_key(xref, TAG_KEY)
        if tag_type != 'name' or tag_value != TAG_VALUE:
            continue
        depth_type, depth_value = doc.xref_get_key(xref, DEPTH_KEY)
        seal_type, seal_value = doc.xref_get_key(xref, SEAL_KEY)
        base_type, base_value = doc.xref_get_key(xref, BASE_SIZE_KEY)
        nonce_type, nonce_value = doc.xref_get_key(xref, NONCE_KEY)
        if depth_type != 'int': raise RuntimeError('PDF self return has an invalid depth field')
        if seal_type != 'string': raise RuntimeError('PDF self return has an invalid seal field')
        if base_type != 'int': raise RuntimeError('PDF self return has an invalid base-size field')
        if nonce_type != 'int': raise RuntimeError('PDF self return requires its stored nonce')
        stored_nonce = validate_nonce(int(nonce_value))
        found.append((xref, int(depth_value), seal_value, int(base_value), stored_nonce))
    return tuple(found)



def _stat_witness(path: Path) -> tuple[int, int, int, int, int, int]:
    st = path.stat()
    return (st.st_dev, st.st_ino, st.st_mode, st.st_size, st.st_mtime_ns, st.st_ctime_ns)


def _regenerated_final(base: bytes, seal: str, depth: int, *, base_size: int, nonce: int) -> bytes:
    """Regenerate exactly one explicit PDF return for verification."""
    fd, tmp = tempfile.mkstemp(prefix='tardisha_pdf_regen_', suffix='.pdf')
    os.close(fd)
    path = Path(tmp)
    try:
        path.write_bytes(base)
        _append_self_revision(path, seal, depth, base_size, nonce=nonce)
        return path.read_bytes()
    finally:
        path.unlink(missing_ok=True)



def _pdf_return_state(pdf: Path, *, identity_name: str) -> dict:
    """Resolve one PDF body and its optional explicit return from one Vāhana read."""
    before = _stat_witness(pdf)
    data = pdf.read_bytes()
    if len(data) != before[3]: raise RuntimeError('source changed while the PDF return state began')
    doc = pymupdf.open(pdf)
    try:
        found = _find_self_xrefs(doc)
        page_count = doc.page_count
    finally:
        doc.close()
    after = _stat_witness(pdf)
    if after != before: raise RuntimeError('source changed during PDF return state resolution')
    if not found:
        return {'has_return': False, 'valid': True, 'physical_size': len(data), 'page_count': page_count, '_physical': data}
    if len(found) != 1: raise TardiSHAError('PDF contains more than one TardiSHA return marker')
    _xref, depth, embedded, base_size, stored_nonce = found[0]
    parse_public_living_domus(embedded)
    if not (0 < base_size < len(data)): raise RuntimeError('PDF self-return declares an impossible body extent')
    base = data[:base_size]
    base_doc = pymupdf.open(stream=base, filetype='pdf')
    try:
        if base_doc.is_repaired: raise RuntimeError('PDF body beneath the self return requires repair')
    finally:
        base_doc.close()
    emission = file_emission_from_bytes(base, identity_name=identity_name, include_filename=True)
    route_witness = source_route_witness_from_emission(emission)
    expected = living_domus_from_emission(emission, depth, nonce=stored_nonce, route_witness=route_witness)
    seal_residual = _byte_difference(embedded, expected)
    regenerated = _regenerated_final(base, expected, depth, base_size=base_size, nonce=stored_nonce)
    revision_residual = sum(a != b for a, b in zip(data, regenerated)) + abs(len(data) - len(regenerated))
    return_residual = seal_residual + revision_residual
    exact_revision = data == regenerated
    source_closed = bool(emission.closure.verifies and emission.closure.truth == 1)
    valid = bool(return_residual == 0 and exact_revision and source_closed)
    return {
        'has_return': True, 'valid': valid, 'source_stability_verified': True,
        'depth': depth, 'base_size': base_size, 'physical_size': len(data),
        'self_revision_bytes': len(data) - base_size, 'page': page_count,
        'seal': embedded, 'expected_seal': expected, 'exact_self_revision': exact_revision,
        '_return_residual': return_residual, '_seal_residual': seal_residual,
        '_revision_residual': revision_residual, '_source_closed': source_closed,
        '_emission': emission, '_route_witness': route_witness, '_nonce': stored_nonce,
        '_base': base, '_physical': data,
    }








def _atomic_replace_bytes(path: Path, body: bytes) -> None:
    fd, tmp_name = tempfile.mkstemp(prefix=f'.{path.name}.', suffix='.part', dir=path.parent)
    temp = Path(tmp_name)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(body); handle.flush(); os.fsync(handle.fileno())
        os.replace(temp, path)
    except Exception:
        temp.unlink(missing_ok=True)
        raise


def remove_embed(pdf_path: str | Path) -> dict:
    pdf = Path(pdf_path).resolve()
    if not pdf.is_file(): raise FileNotFoundError(pdf)
    state = _pdf_return_state(pdf, identity_name=pdf.name)
    if not state['has_return']: raise TardiSHAError('PDF contains no GrimChain self-return')
    if not state['valid']: raise TardiSHAError('PDF contains a GrimChain return that does not close')
    _atomic_replace_bytes(pdf, state['_base'])
    return {key: value for key, value in state.items() if not key.startswith('_')}



def grimchain_for_pdf(pdf_path: str | Path, depth: int, *, nonce: int = 0) -> str:
    """Return the current GrimChain through one exact verified PDF self-return."""
    pdf = Path(pdf_path).resolve()
    if not pdf.is_file(): raise FileNotFoundError(pdf)
    state = _pdf_return_state(pdf, identity_name=pdf.name)
    return_nonce = validate_nonce(nonce)
    if not state['has_return']:
        return living_domus_for_source(
            pdf, depth, kind='file', nonce=return_nonce, include_filename=True
        )
    if not state['valid']:
        raise TardiSHAError('PDF contains a GrimChain return that does not close')
    return living_domus_from_emission(
        state['_emission'], depth, nonce=return_nonce, route_witness=state['_route_witness']
    )


def embed(pdf_path: str | Path, depth: int, *, nonce: int = 0) -> dict:
    pdf = Path(pdf_path).resolve()
    if not pdf.is_file(): raise FileNotFoundError(pdf)
    state = _pdf_return_state(pdf, identity_name=pdf.name)
    return_nonce = validate_nonce(nonce)
    if state['has_return']:
        if not state['valid']: raise TardiSHAError('PDF contains a GrimChain return that does not close')
        base = state['_base']
        seal = living_domus_from_emission(
            state['_emission'], depth, nonce=return_nonce, route_witness=state['_route_witness']
        )
    else:
        base = state['_physical']
        seal = living_domus_for_source(
            pdf, depth, kind='file', nonce=return_nonce, include_filename=True
        )
    base_size = len(base)
    base_doc = pymupdf.open(stream=base, filetype='pdf')
    try: page = base_doc.page_count + 1
    finally: base_doc.close()
    final = _regenerated_final(base, seal, depth, base_size=base_size, nonce=return_nonce)
    fd, tmp_name = tempfile.mkstemp(prefix=f'.{pdf.name}.', suffix='.part', dir=pdf.parent)
    temp = Path(tmp_name)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(final); handle.flush(); os.fsync(handle.fileno())
        result = _pdf_return_state(temp, identity_name=pdf.name)
        if not result['has_return'] or not result['valid']: raise RuntimeError('PDF failed exact self-return verification')
        os.replace(temp, pdf)
    except Exception:
        temp.unlink(missing_ok=True)
        raise
    result['page'] = page
    return {key: value for key, value in result.items() if not key.startswith('_')}


