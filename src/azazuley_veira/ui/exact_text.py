from __future__ import annotations

import uharfbuzz as hb
from collections import OrderedDict
from dataclasses import dataclass, field
import unicodedata
from enum import IntEnum
from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QMarginsF, QPointF, QRectF, QSize, QSizeF, Qt, Signal
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication, QKeySequence, QPageLayout, QPageSize, QPainter, QPainterPath, QPalette, QPdfWriter, QTextCursor
from PySide6.QtWidgets import QAbstractScrollArea, QMenu
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

from azazuley_veira.config.font_runtime import DEFAULT_POINT_SIZE, grimchain_display_codepoints, grimchain_face_for_character, physical_font_family, system_font_file_for_codepoint, system_font_file_for_family

try:
    from ._azuzaley_kernel import visual_order as _compiled_visual_order
except ImportError as exc:
    raise RuntimeError("Azuzaley requires the compiled exact-layout index kernel") from exc

_BIDI_CLASS_CODES = {
    "L": 0,
    "R": 1,
    "AL": 2,
    "ON": 3,
    "NSM": 4,
    "EN": 5,
    "CS": 6,
    "ES": 7,
    "ET": 8,
    "WS": 9,
}
_ALLOWED_BIDI_CLASSES = frozenset(_BIDI_CLASS_CODES)


@lru_cache(maxsize=2048)
def _natural_visual_order(text: str) -> tuple[tuple[int, ...], tuple[int, ...]]:
    classes = tuple(unicodedata.bidirectional(glyph) or "ON" for glyph in text)
    unsupported = tuple(sorted(set(classes) - _ALLOWED_BIDI_CLASSES))
    if unsupported:
        raise RuntimeError(f"unsupported exact-surface bidi classes: {unsupported!r}")
    return _compiled_visual_order(tuple(_BIDI_CLASS_CODES[value] for value in classes))


def qt_utf16_units(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2

def _qt_boundaries(text: str) -> tuple[int, ...]:
    values=[0]; total=0
    for ch in text:
        total += 2 if ord(ch)>0xFFFF else 1
        values.append(total)
    return tuple(values)

def _py_index_for_qt(text: str, qt_position: int) -> int:
    if qt_position < 0 or qt_position > qt_utf16_units(text): raise ValueError(f"UTF-16 position outside text: {qt_position}")
    total=0
    for i,ch in enumerate(text):
        if total == qt_position: return i
        total += qt_utf16_units(ch)
        if total > qt_position: raise ValueError(f"UTF-16 position splits a code point: {qt_position}")
    if total == qt_position: return len(text)
    raise ValueError(f"UTF-16 position outside text: {qt_position}")

def _slice_qt(text: str, start: int, end: int) -> str:
    return text[_py_index_for_qt(text,start):_py_index_for_qt(text,end)]

class _PainterPathPen(BasePen):
    def __init__(self, glyph_set):
        super().__init__(glyph_set)
        self.path = QPainterPath()

    def _moveTo(self, point): self.path.moveTo(float(point[0]), float(point[1]))
    def _lineTo(self, point): self.path.lineTo(float(point[0]), float(point[1]))
    def _curveToOne(self, p1, p2, p3):
        self.path.cubicTo(float(p1[0]), float(p1[1]), float(p2[0]), float(p2[1]), float(p3[0]), float(p3[1]))
    def _qCurveToOne(self, p1, p2):
        self.path.quadTo(float(p1[0]), float(p1[1]), float(p2[0]), float(p2[1]))
    def _closePath(self): self.path.closeSubpath()


@dataclass(frozen=True, slots=True)
class _OutlineFontResource:
    font: TTFont
    glyph_set: object
    glyph_order: tuple[str, ...]
    upem: int


@lru_cache(maxsize=128)
def _outline_font_resource(font_file: Path) -> _OutlineFontResource:
    font=TTFont(font_file, lazy=False)
    return _OutlineFontResource(font,font.getGlyphSet(),tuple(font.getGlyphOrder()),int(font['head'].unitsPerEm))


@lru_cache(maxsize=8192)
def _glyph_path(font_file: Path, glyph_id: int) -> QPainterPath:
    resource=_outline_font_resource(font_file)
    try:
        glyph_name=resource.glyph_order[glyph_id]
    except IndexError as exc:
        raise RuntimeError(f"glyph id is outside physical font: {font_file} -> {glyph_id}") from exc
    pen=_PainterPathPen(resource.glyph_set)
    resource.glyph_set[glyph_name].draw(pen)
    return pen.path


@dataclass(frozen=True, slots=True)
class ExactGlyphRun:
    font_file: Path
    glyph_indexes: tuple[int, ...]
    positions: tuple[QPointF, ...]
    pixel_size: float
    upem: int

    def glyphIndexes(self): return list(self.glyph_indexes)

    def paint(self, painter: QPainter, origin: QPointF) -> None:
        scale=self.pixel_size/self.upem
        for glyph_id,position in zip(self.glyph_indexes,self.positions):
            painter.save()
            painter.translate(origin.x()+position.x(),origin.y()+position.y())
            painter.scale(scale,-scale)
            painter.drawPath(_glyph_path(self.font_file,glyph_id))
            painter.restore()


@dataclass(frozen=True, slots=True)
class _ExactFontResource:
    face: hb.Face
    font: hb.Font
    upem: int


def _open_exact_font_resource(font_file: Path) -> _ExactFontResource:
    try:
        face = hb.Face(font_file.read_bytes())
    except OSError as exc:
        raise RuntimeError(f"HarfBuzz could not open authored font file: {font_file}") from exc
    upem = int(face.upem)
    if upem <= 0:
        raise RuntimeError(f"authored font has invalid units-per-em: {font_file}")
    font = hb.Font(face)
    hb.ot_font_set_funcs(font)
    font.scale = (upem, upem)
    return _ExactFontResource(face, font, upem)


def _close_exact_font_resource(resource: _ExactFontResource) -> None:
    del resource


def _shape_exact_font(font_file: Path, text: str, pixel_size: float, resource: _ExactFontResource | None = None) -> tuple[ExactGlyphRun,float,float,float]:
    if not text: raise ValueError("exact shaping requires non-empty text")
    owned_resource=resource is None
    r=_open_exact_font_resource(font_file) if owned_resource else resource
    try:
        buffer=hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        hb.shape(r.font,buffer)
        infos=buffer.glyph_infos
        positions=buffer.glyph_positions
        scale=pixel_size/r.upem
        gids=[]; points=[]; x=0.0; y=0.0
        for info,position in zip(infos,positions):
            gid=int(info.codepoint)
            if gid==0: raise RuntimeError(f"authored font produced missing glyph for {text!r}: {font_file}")
            gids.append(gid)
            points.append(QPointF(x+position.x_offset*scale,-(y+position.y_offset*scale)))
            x += position.x_advance*scale
            y += position.y_advance*scale
        extents=r.font.get_font_extents("ltr")
        if extents is None:
            raise RuntimeError(f"HarfBuzz could not read font extents: {font_file}")
        run=ExactGlyphRun(font_file,tuple(gids),tuple(points),float(pixel_size),r.upem)
        return run,max(0.0,float(extents.ascender)*scale),max(0.0,-float(extents.descender)*scale),abs(float(x))
    finally:
        if owned_resource:
            _close_exact_font_resource(r)

@dataclass(frozen=True, slots=True)
class ExactSourceRun:
    qt_start:int; text:str; font_file:Path; exact:bool=True
    qt_units:int=field(init=False)
    qt_boundaries:tuple[int,...]=field(init=False)
    def __post_init__(self):
        boundaries=_qt_boundaries(self.text)
        object.__setattr__(self,'qt_boundaries',boundaries)
        object.__setattr__(self,'qt_units',boundaries[-1])
    @property
    def qt_end(self)->int: return self.qt_start+self.qt_units

@dataclass(frozen=True, slots=True)
class ExactPlacedRun:
    qt_start:int; qt_end:int; text:str; font_file:Path; glyph_run:ExactGlyphRun; x:float; baseline:float; advance:float; ascent:float; descent:float; line_index:int; exact:bool; bidi_level:int=0

@dataclass(frozen=True, slots=True)
class ExactLayoutModel:
    text:str
    runs:tuple[ExactPlacedRun,...]
    width:float
    height:float
    cursor_rects:tuple[tuple[int,QRectF],...]
    cantillation_text:str=""
    cantillation_source_positions:tuple[int,...]=()
    page_rects:tuple[QRectF,...]=()
    content_page_count:int=0

    def __post_init__(self) -> None:
        if len(self.cantillation_text) != len(self.cantillation_source_positions):
            raise ValueError("Cantillation text/source mapping extent mismatch")
        source_by_qt: dict[int, str] = {}
        source_qt = 0
        for character in self.text:
            source_by_qt[source_qt] = character
            source_qt += 2 if ord(character)>0xFFFF else 1
        for character, visual_source_qt in zip(
            self.cantillation_text, self.cantillation_source_positions
        ):
            if source_by_qt.get(visual_source_qt) != character:
                raise ValueError("Cantillation visual position is detached from Prosody source text")

    @property
    def visual_text(self) -> str:
        return self.cantillation_text

    @property
    def visual_source_positions(self) -> tuple[int, ...]:
        return self.cantillation_source_positions

    @property
    def cantillation(self) -> tuple[tuple[str, int], ...]:
        return tuple(zip(self.cantillation_text, self.cantillation_source_positions))

_SHAPE_CACHE_LIMIT = 8192
_SHAPE_CACHE: OrderedDict[tuple[Path, str, float], tuple[ExactGlyphRun, float, float, float]] = OrderedDict()


class ExactHarfBuzzLayout:
    def __init__(self,pixel_size:float):
        if pixel_size<=0: raise ValueError("exact layout pixel size must be positive")
        self.pixel_size=float(pixel_size)
        self.resources={}
    def shape(self,source:ExactSourceRun):
        key=(source.font_file,source.text,round(self.pixel_size,4))
        shape=_SHAPE_CACHE.get(key)
        if shape is not None:
            _SHAPE_CACHE.move_to_end(key)
            return shape
        resource=self.resources.get(source.font_file)
        if resource is None:
            resource=_open_exact_font_resource(source.font_file)
            self.resources[source.font_file]=resource
        shape=_shape_exact_font(source.font_file,source.text,self.pixel_size,resource)
        _SHAPE_CACHE[key]=shape
        if len(_SHAPE_CACHE)>_SHAPE_CACHE_LIMIT:
            _SHAPE_CACHE.popitem(last=False)
        return shape
    def close(self):
        for resource in self.resources.values():
            _close_exact_font_resource(resource)
        self.resources.clear()
    def layout(self,text:str,sources:tuple[ExactSourceRun,...],width:float|None,force_ltr:bool=False)->ExactLayoutModel:
        if width is not None and width<=0: raise ValueError("exact layout width must be positive")
        text_qt_units=sources[-1].qt_end if sources else 0
        lines=[[]]; widths=[0.0]

        def wrapped_parts(source: ExactSourceRun):
            shape=self.shape(source)
            if width is None or shape[3] <= width or not source.text:
                return ((source,shape),)
            out=[]; remaining=source.text; source_qt=source.qt_start
            while remaining:
                whole=ExactSourceRun(source_qt,remaining,source.font_file,source.exact)
                whole_shape=self.shape(whole)
                if whole_shape[3] <= width:
                    out.append((whole,whole_shape)); break
                low=1; high=len(remaining); best=1
                while low <= high:
                    mid=(low+high)//2
                    probe=ExactSourceRun(source_qt,remaining[:mid],source.font_file,source.exact)
                    probe_shape=self.shape(probe)
                    if probe_shape[3] <= width:
                        best=mid; low=mid+1
                    else:
                        high=mid-1
                whitespace=[index+1 for index,character in enumerate(remaining[:best]) if character.isspace()]
                cut=whitespace[-1] if whitespace else best
                part=ExactSourceRun(source_qt,remaining[:cut],source.font_file,source.exact)
                part_shape=self.shape(part)
                if part_shape[3] > width and cut != best:
                    cut=best
                    part=ExactSourceRun(source_qt,remaining[:cut],source.font_file,source.exact)
                    part_shape=self.shape(part)
                out.append((part,part_shape))
                source_qt += part.qt_units
                remaining=remaining[cut:]
            return tuple(out)

        def append_wrapped(source: ExactSourceRun):
            for part,shape in wrapped_parts(source):
                if width is not None and lines[-1] and widths[-1]+shape[3]>width:
                    lines.append([]); widths.append(0.0)
                lines[-1].append((part,shape)); widths[-1]+=shape[3]

        for src in sources:
            if "\n" not in src.text:
                append_wrapped(src)
                continue
            source_qt=src.qt_start
            parts=src.text.split("\n")
            for part_index,segment in enumerate(parts):
                if segment:
                    part=ExactSourceRun(source_qt,segment,src.font_file,src.exact)
                    append_wrapped(part)
                    source_qt += part.qt_units
                if part_index < len(parts)-1:
                    source_qt += 1
                    lines.append([]); widths.append(0.0)
        probe_file=system_font_file_for_family('Noto Sans')
        _p,da,dd,_a=self.shape(ExactSourceRun(0,'M',probe_file,False))
        placed=[]; cursors={}; y=0.0; maxw=0.0; full_visual=[]; full_visual_sources=[]
        for li,items in enumerate(lines):
            logical=[]
            item_ranges=[]
            for item_index,(src,shape) in enumerate(items):
                begin=len(logical)
                for char_index,ch in enumerate(src.text):
                    logical.append((ch,src.qt_start+src.qt_boundaries[char_index],item_index))
                item_ranges.append((begin,len(logical)))
            line_text=''.join(cell[0] for cell in logical)
            if force_ltr:
                visual_order=tuple(range(len(logical))); levels=tuple(0 for _ in logical)
            else:
                visual_order,levels=_natural_visual_order(line_text)
            full_visual.extend(logical[i][0] for i in visual_order)
            full_visual_sources.extend(logical[i][1] for i in visual_order)
            l2v={logical_index:visual_index for visual_index,logical_index in enumerate(visual_order)}
            ordered=[]
            for item_index,(src,shape) in enumerate(items):
                begin,end=item_ranges[item_index]
                visual_key=min((l2v[k] for k in range(begin,end)),default=item_index)
                level=levels[begin] if begin < len(levels) else 0
                ordered.append((visual_key,src,shape,level))
            ordered.sort(key=lambda item:item[0])
            asc=max((shape[1] for _key,_src,shape,_level in ordered),default=da)
            desc=max((shape[2] for _key,_src,shape,_level in ordered),default=dd)
            baseline=y+asc; x=0.0
            if not ordered:
                cursors.setdefault(0 if li==0 else text_qt_units,QRectF(0,y,1,asc+desc))
            for _key,src,shape,level in ordered:
                gr,ra,rd,adv=shape
                start=src.qt_start; end=src.qt_end
                placed.append(ExactPlacedRun(start,end,src.text,src.font_file,gr,x,baseline,adv,ra,rd,li,src.exact,level))
                bounds=src.qt_boundaries
                count=max(1,len(bounds)-1)
                for py,rel in enumerate(bounds):
                    off=adv*(py/count)
                    cx=x+off if not (level&1) else x+adv-off
                    cursors[start+rel]=QRectF(cx,y,1,asc+desc)
                x+=adv
            maxw=max(maxw,x); y+=asc+desc
        return ExactLayoutModel(text,tuple(sorted(placed,key=lambda r:r.qt_start)),maxw,max(y,da+dd),tuple(sorted(cursors.items())),''.join(full_visual),tuple(full_visual_sources))



class _ExactCursor:
    def __init__(self,surface:'ExactFontTextEdit',position:int|None=None,anchor:int|None=None):
        self._surface=surface; end=qt_utf16_units(surface.toPlainText()); self._position=end if position is None else position; self._anchor=self._position if anchor is None else anchor
    def position(self): return self._position
    def anchor(self): return self._anchor
    def hasSelection(self): return self._position != self._anchor
    def clearSelection(self): self._anchor=self._position
    def selectedText(self):
        a,b=sorted((self._position,self._anchor)); return _slice_qt(self._surface.toPlainText(),a,b).replace('\n','\u2029')
    def setPosition(self,pos,mode=QTextCursor.MoveMode.MoveAnchor):
        _py_index_for_qt(self._surface.toPlainText(),pos)
        if mode != QTextCursor.MoveMode.KeepAnchor: self._anchor=pos
        self._position=pos
    def select(self,selection):
        if selection != QTextCursor.SelectionType.Document: raise NotImplementedError
        self._anchor=0; self._position=qt_utf16_units(self._surface.toPlainText())
    def movePosition(self,op,mode=QTextCursor.MoveMode.MoveAnchor,n=1):
        b=_qt_boundaries(self._surface.toPlainText()); i=b.index(self._position)
        if op==QTextCursor.MoveOperation.Start: target=b[0]
        elif op==QTextCursor.MoveOperation.End: target=b[-1]
        elif op in (QTextCursor.MoveOperation.Left,QTextCursor.MoveOperation.PreviousCharacter): target=b[max(0,i-n)]
        elif op in (QTextCursor.MoveOperation.Right,QTextCursor.MoveOperation.NextCharacter): target=b[min(len(b)-1,i+n)]
        else: return False
        self.setPosition(target,mode); return True
    def insertText(self,text): self._surface._replace_selection(self,text)

class ExactFontTextEdit(QAbstractScrollArea):
    textChanged=Signal()
    class LineWrapMode(IntEnum): NoWrap=0; WidgetWidth=1
    def __init__(self,parent=None):
        super().__init__(parent); self._text=''; self._qt_to_py={0:0}; self._text_qt_units=0; self._exact_spans=[]; self._cursor_position=0; self._cursor_anchor=0; self._read_only=False; self._line_wrap_mode=self.LineWrapMode.WidgetWidth; self._alignment=Qt.AlignmentFlag.AlignLeft; self._force_ltr=False; self._wheel_angle_remainder=0; self._tab_changes_focus=False; self._margin=4.0; self._layout_model=None; self._layout_key=None; self._point_size=float(DEFAULT_POINT_SIZE); self._default_font_file=system_font_file_for_family('Noto Sans'); self._scripture_pages=False; self._scripture_page_height=0.0; self._scripture_page_gap=24.0; self._scripture_top_margin=20.0; self._scripture_bottom_margin=20.0; self._scripture_minimum_pages=1; self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    def setDefaultFontFile(self,p): self._default_font_file=Path(p); self._invalidate_layout()
    def defaultFontFile(self): return self._default_font_file
    def documentMargin(self): return self._margin
    def setDocumentMargin(self,m):
        margin=max(0.0,float(m))
        if margin != self._margin:
            self._margin=margin
            self._invalidate_layout()
    def _rebuild_text_index(self):
        qt=0; mapping={0:0}
        for py,ch in enumerate(self._text, start=1):
            qt+=2 if ord(ch)>0xFFFF else 1; mapping[qt]=py
        self._qt_to_py=mapping
        self._text_qt_units=qt
        return qt
    def setPlainText(self,text):
        text=str(text)
        if self.property('_strict_grimchain') and any(ord(ch) not in grimchain_display_codepoints() for ch in text):
            raise ValueError('GrimChain surface accepts only authored GrimChain code points')
        self._text=text; self._exact_spans.clear(); end=self._rebuild_text_index(); self._cursor_position=min(self._cursor_position,end); self._cursor_anchor=self._cursor_position; self._invalidate_layout(); self.textChanged.emit()
    def toPlainText(self): return self._text
    def clear(self): self.setPlainText('')
    def setReadOnly(self,v): self._read_only=bool(v)
    def isReadOnly(self): return self._read_only
    def setLineWrapMode(self,mode): self._line_wrap_mode=self.LineWrapMode(mode.value if hasattr(mode,'value') else int(mode)); self._invalidate_layout()
    def setForcedLeftToRightLayout(self,v):
        force_ltr=bool(v)
        if force_ltr != self._force_ltr:
            self._force_ltr=force_ltr
            self._invalidate_layout()
    def setScripturePageLayout(self,enabled:bool,*,page_height:float=0.0,page_gap:float=24.0,top_margin:float=20.0,bottom_margin:float=20.0):
        enabled=bool(enabled)
        page_height=max(0.0,float(page_height))
        top_margin=max(0.0,float(top_margin))
        bottom_margin=max(0.0,float(bottom_margin))
        if enabled and page_height <= top_margin + bottom_margin:
            raise ValueError('scripture page height must exceed its vertical text margins')
        page_gap=max(0.0,float(page_gap))
        geometry=(enabled,page_height,page_gap,top_margin,bottom_margin)
        current=(self._scripture_pages,self._scripture_page_height,self._scripture_page_gap,self._scripture_top_margin,self._scripture_bottom_margin)
        if geometry != current:
            self._scripture_pages=enabled
            self._scripture_page_height=page_height
            self._scripture_page_gap=page_gap
            self._scripture_top_margin=top_margin
            self._scripture_bottom_margin=bottom_margin
            self._invalidate_layout()
    def setScriptureMinimumPageCount(self,count:int):
        count=max(1,int(count))
        if count != self._scripture_minimum_pages:
            self._scripture_minimum_pages=count
            self._invalidate_layout()
    def scripturePageLayout(self): return self._scripture_pages
    def scripturePageGeometry(self): return self._scripture_page_height,self._scripture_page_gap
    def scriptureContentPageCount(self): return self._layout().content_page_count if self._scripture_pages else 0
    def lineWrapMode(self): return self._line_wrap_mode
    def setTabChangesFocus(self,v): self._tab_changes_focus=bool(v)
    def setAlignment(self,a):
        if a != self._alignment:
            self._alignment=a
            self._invalidate_layout()
    def textCursor(self): return _ExactCursor(self,self._cursor_position,self._cursor_anchor)
    def setTextCursor(self,c):
        if not isinstance(c,_ExactCursor) or c._surface is not self: raise TypeError('cursor does not belong to exact surface')
        self._cursor_position=c.position(); self._cursor_anchor=c.anchor(); self.ensureCursorVisible(); self.viewport().update()
    def moveCursor(self,op,mode=QTextCursor.MoveMode.MoveAnchor): c=self.textCursor(); c.movePosition(op,mode); self.setTextCursor(c)
    def insertPlainText(self,text):
        if self._read_only: return
        c=self.textCursor(); self._replace_selection(c,text); self.setTextCursor(c)
    def selectAll(self): c=self.textCursor(); c.select(QTextCursor.SelectionType.Document); self.setTextCursor(c)
    def copy(self):
        t=self.textCursor().selectedText().replace('\u2029','\n')
        if t: QGuiApplication.clipboard().setText(t)
    def cut(self):
        if self._read_only:return
        self.copy(); c=self.textCursor(); self._replace_selection(c,''); self.setTextCursor(c)
    def paste(self):
        if not self._read_only:self.insertPlainText(QGuiApplication.clipboard().text())
    def _replace_selection(self,c,replacement):
        if self.property('_strict_grimchain') and any(ord(ch) not in grimchain_display_codepoints() for ch in replacement):
            return
        a,b=sorted((c.position(),c.anchor())); pa=self._qt_to_py[a]; pb=self._qt_to_py[b]; self._text=self._text[:pa]+replacement+self._text[pb:]; self._exact_spans.clear(); np=a+qt_utf16_units(replacement); self._rebuild_text_index(); c._position=np; c._anchor=np; self._cursor_position=np; self._cursor_anchor=np; self._invalidate_layout(); self.textChanged.emit()
    def textForUtf16Range(self,a,b):
        try: return self._text[self._qt_to_py[a]:self._qt_to_py[b]]
        except KeyError as exc: raise ValueError(f'UTF-16 range splits a code point: {(a,b)!r}') from exc
    def clear_exact_spans(self): self._exact_spans.clear(); self._invalidate_layout()
    def add_exact_font_span(self,qt_start,text,family,font_file):
        del family
        if not text:return
        physical_file=font_file if isinstance(font_file,Path) else Path(font_file)
        run=ExactSourceRun(qt_start,text,physical_file,True)
        if self.textForUtf16Range(qt_start,run.qt_end)!=text: raise ValueError('exact font span text/provenance mismatch')
        self._exact_spans.append(run)
        self._layout_model=None; self._layout_key=None
    def exact_spans(self):
        return tuple(sorted(self._exact_spans,key=lambda span:span.qt_start))
    def exact_span_at(self,pos):
        for s in self.exact_spans():
            if s.qt_start<=pos<s.qt_end:return s
        return None
    def exact_font_family_at(self,pos):
        s=self.exact_span_at(pos); f=self._default_font_file if s is None else s.font_file; return physical_font_family(f)
    def setPointSizeF(self,point_size):
        point_size=float(point_size)
        if point_size<=0: raise ValueError('exact font surface requires positive point size')
        if point_size != self._point_size:
            self._point_size=point_size
            self._invalidate_layout()
    def pointSizeF(self): return self._point_size
    def _pixel_size(self): return self._point_size*self.logicalDpiY()/72.0
    def _source_runs(self):
        spans=tuple(sorted(self._exact_spans,key=lambda span:span.qt_start))
        for left,right in zip(spans,spans[1:]):
            if left.qt_end>right.qt_start: raise ValueError('exact font spans overlap')
        out=[]; q=0; p=0; i=0; total=self._text_qt_units
        while p<len(self._text):
            s=spans[i] if i<len(spans) else None
            if s is not None and q==s.qt_start: out.append(s); p+=len(s.text); q=s.qt_end; i+=1; continue
            nq=s.qt_start if s is not None else total; sq=q
            try:
                target_p=self._qt_to_py[nq]
            except KeyError as exc:
                raise ValueError(f'UTF-16 source-run boundary splits a code point: {nq}') from exc
            body=self._text[p:target_p]
            if body: out.append(ExactSourceRun(sq,body,self._default_font_file,False))
            p=target_p; q=nq
        return tuple(out)
    def _source_runs_for_qt_range(self,sources,start,end):
        out=[]
        for source in sources:
            left=max(start,source.qt_start); right=min(end,source.qt_end)
            if left>=right: continue
            local_start=left-source.qt_start; local_end=right-source.qt_start
            body=_slice_qt(source.text,local_start,local_end)
            out.append(ExactSourceRun(left,body,source.font_file,source.exact))
        return tuple(out)
    def _content_width(self): return None if self._line_wrap_mode==self.LineWrapMode.NoWrap else max(1.0,float(self.viewport().width())-self._margin*2)
    def _measure_scripture_paragraphs(self,layout,sources,width):
        key=(
            self._text,
            tuple((source.qt_start,source.text,source.font_file,source.exact) for source in sources),
            round(float(width),4),
            round(self._pixel_size(),4),
            self._force_ltr,
        )
        cached=getattr(self,'_scripture_measurement_cache',None)
        if cached is not None and cached[0]==key:
            return cached[1]
        paragraph_ranges=[]; start=0
        for paragraph in self._text.split('\n'):
            end=start+qt_utf16_units(paragraph)
            paragraph_ranges.append((start,end))
            start=end+1
        measured=[]
        probe_height=self.defaultLineHeight()
        for start,end in paragraph_ranges:
            paragraph_sources=self._source_runs_for_qt_range(sources,start,end)
            if paragraph_sources:
                model=layout.layout(self._text,paragraph_sources,width,self._force_ltr)
                height=max(probe_height,model.height)
            else:
                model=None; height=probe_height
            measured.append((start,end,model,height))
        result=(tuple(measured),probe_height)
        self._scripture_measurement_cache=(key,result)
        return result
    def _scripture_layout(self,layout,sources,width):
        if width is None:
            width=max(1.0,float(self.viewport().width())-self._margin*2)
        measured,probe_height=self._measure_scripture_paragraphs(layout,sources,width)
        tallest=max((height for _start,_end,_model,height in measured),default=probe_height)
        page_height=self._scripture_page_height
        if self._scripture_top_margin+tallest+self._scripture_bottom_margin>page_height:
            raise ValueError('scripture paragraph exceeds the shared page geometry')
        usable_bottom=page_height-self._scripture_bottom_margin
        page_rects=[]; placed=[]; cursors={}; full_visual=[]; full_visual_sources=[]
        page_index=0; page_origin=0.0; y_in_page=self._scripture_top_margin; line_offset=0; max_width=0.0
        page_rects.append(QRectF(0.0,page_origin,width,page_height))
        for start,end,model,height in measured:
            if y_in_page>self._scripture_top_margin and y_in_page+height>usable_bottom:
                page_index+=1
                page_origin=page_index*(page_height+self._scripture_page_gap)
                page_rects.append(QRectF(0.0,page_origin,width,page_height))
                y_in_page=self._scripture_top_margin
            dy=page_origin+y_in_page
            if model is None:
                cursors.setdefault(start,QRectF(0.0,dy,1.0,height))
                cursors.setdefault(end,QRectF(0.0,dy,1.0,height))
            else:
                for run in model.runs:
                    placed.append(ExactPlacedRun(run.qt_start,run.qt_end,run.text,run.font_file,run.glyph_run,run.x,run.baseline+dy,run.advance,run.ascent,run.descent,run.line_index+line_offset,run.exact,run.bidi_level))
                for position,rect in model.cursor_rects:
                    if start<=position<=end:
                        cursors[position]=rect.translated(0.0,dy)
                full_visual.append(model.cantillation_text)
                full_visual_sources.extend(model.cantillation_source_positions)
                if model.runs:
                    line_offset+=max(run.line_index for run in model.runs)+1
                max_width=max(max_width,model.width)
            y_in_page+=height
        content_page_count=len(page_rects)
        while len(page_rects) < self._scripture_minimum_pages:
            page_origin=len(page_rects)*(page_height+self._scripture_page_gap)
            page_rects.append(QRectF(0.0,page_origin,width,page_height))
        document_height=page_rects[-1].bottom() if page_rects else page_height
        return ExactLayoutModel(self._text,tuple(sorted(placed,key=lambda run:run.qt_start)),max(max_width,width),document_height,tuple(sorted(cursors.items())),''.join(full_visual),tuple(full_visual_sources),tuple(page_rects),content_page_count)
    def _layout(self):
        key=(self._text,tuple((s.qt_start,s.text,s.font_file) for s in self._exact_spans),round(self._pixel_size(),4),self._content_width(),int(self._alignment),self._force_ltr,self._scripture_pages,round(self._scripture_page_height,4),round(self._scripture_page_gap,4),round(self._scripture_top_margin,4),round(self._scripture_bottom_margin,4),self._scripture_minimum_pages)
        if self._layout_model is not None and self._layout_key==key:return self._layout_model
        layout=ExactHarfBuzzLayout(self._pixel_size())
        try:
            sources=self._source_runs()
            if self._scripture_pages:
                m=self._scripture_layout(layout,sources,self._content_width())
            else:
                m=layout.layout(self._text,sources,self._content_width(),self._force_ltr)
        finally:
            layout.close()
        if self._alignment & (Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignRight) and m.runs:
            by={}
            for r in m.runs: by.setdefault(r.line_index,[]).append(r)
            shifted=[]; shifts={}; vw=max(1.0,float(self.viewport().width())-self._margin*2)
            for line,runs in by.items():
                line_left=min(r.x for r in runs); line_right=max(r.x+r.advance for r in runs)
                if self._alignment & Qt.AlignmentFlag.AlignRight:
                    sh=max(0.0,vw-line_right)
                else:
                    sh=max(0.0,(vw-(line_right-line_left))/2-line_left)
                for r in runs: shifted.append(ExactPlacedRun(r.qt_start,r.qt_end,r.text,r.font_file,r.glyph_run,r.x+sh,r.baseline,r.advance,r.ascent,r.descent,r.line_index,r.exact,r.bidi_level))
                for pos,rect in m.cursor_rects:
                    if any(r.qt_start<=pos<=r.qt_end for r in runs): shifts[pos]=sh
            m=ExactLayoutModel(m.text,tuple(shifted),m.width,m.height,tuple((pos,rect.translated(shifts.get(pos,0),0)) for pos,rect in m.cursor_rects),m.cantillation_text,m.cantillation_source_positions,m.page_rects,m.content_page_count)
        self._layout_model=m; self._layout_key=key; self._update_scrollbars(m); return m
    def _invalidate_layout(self): self._layout_model=None; self._layout_key=None; self.viewport().update()
    def _update_scrollbars(self,m):
        w=int(m.width+self._margin*2+0.999); h=int(m.height+self._margin*2+0.999); self.horizontalScrollBar().setRange(0,max(0,w-self.viewport().width())); self.horizontalScrollBar().setPageStep(self.viewport().width()); self.verticalScrollBar().setRange(0,max(0,h-self.viewport().height())); self.verticalScrollBar().setPageStep(self.viewport().height())
    def defaultLineHeight(self):
        layout=ExactHarfBuzzLayout(self._pixel_size())
        try:
            _r,a,d,_v=layout.shape(ExactSourceRun(0,'M',self._default_font_file,False))
            return a+d
        finally:
            layout.close()
    def documentExtent(self): m=self._layout(); return QSizeF(m.width+self._margin*2,m.height+self._margin*2)
    def exactLayoutModel(self): return self._layout()
    def cursorRect(self,cursor=None):
        m=self._layout(); pos=self._cursor_position if cursor is None else cursor.position(); rect=dict(m.cursor_rects).get(pos,QRectF(0,0,1,self.defaultLineHeight())); return rect.translated(self._margin-self.horizontalScrollBar().value(),self._margin-self.verticalScrollBar().value()).toRect()
    def ensureCursorVisible(self):
        r=self.cursorRect(); hs=self.horizontalScrollBar(); vs=self.verticalScrollBar()
        if r.left()<0: hs.setValue(hs.value()+r.left())
        elif r.right()>self.viewport().width(): hs.setValue(hs.value()+r.right()-self.viewport().width())
        if r.top()<0: vs.setValue(vs.value()+r.top())
        elif r.bottom()>self.viewport().height(): vs.setValue(vs.value()+r.bottom()-self.viewport().height())
    def _hit_test(self,p):
        m=self._layout(); c=QPointF(p.x()+self.horizontalScrollBar().value()-self._margin,p.y()+self.verticalScrollBar().value()-self._margin); best=0; bd=float('inf')
        for pos,r in m.cursor_rects:
            d=abs(c.x()-r.x())+abs(c.y()-(r.top()+r.height()/2))*2
            if d<bd:bd=d;best=pos
        return best
    def resizeEvent(self,e): super().resizeEvent(e); self._invalidate_layout()
    def wheelEvent(self,e):
        pixel_delta=e.pixelDelta().y()
        if pixel_delta:
            bar=self.verticalScrollBar(); bar.setValue(bar.value()-pixel_delta); e.accept(); return
        angle_delta=e.angleDelta().y()
        if angle_delta:
            self._wheel_angle_remainder += angle_delta
            steps=int(self._wheel_angle_remainder/120)
            if steps:
                self._wheel_angle_remainder -= steps*120
                line=max(1,int(round(self.defaultLineHeight())))
                bar=self.verticalScrollBar(); bar.setValue(bar.value()-steps*line)
            e.accept(); return
        super().wheelEvent(e)
    def selectionRectangles(self):
        m=self._layout(); ss,se=sorted((self._cursor_position,self._cursor_anchor)); rects=[]
        if ss==se:return tuple(rects)
        for r in m.runs:
            if ss>=r.qt_end or se<=r.qt_start:continue
            ls=max(ss,r.qt_start); le=min(se,r.qt_end)
            if ls==r.qt_start and le==r.qt_end:
                pa=0.0; ca=r.advance
            else:
                bounds=_qt_boundaries(r.text)
                total=max(1,len(bounds)-1)
                start_rel=ls-r.qt_start; end_rel=le-r.qt_start
                start_index=next((i for i,value in enumerate(bounds) if value==start_rel),0)
                end_index=next((i for i,value in enumerate(bounds) if value==end_rel),total)
                pa=r.advance*(start_index/total)
                ca=r.advance*((end_index-start_index)/total)
            sx=r.x+pa if not (r.bidi_level&1) else r.x+r.advance-pa-ca
            rects.append(QRectF(sx,r.baseline-r.ascent,ca,r.ascent+r.descent))
        return tuple(rects)
    def paintEvent(self,e):
        m=self._layout(); p=QPainter(self.viewport()); dirty=e.rect(); dirty_f=QRectF(dirty); p.setClipRect(dirty); p.fillRect(dirty,self.palette().color(QPalette.ColorRole.Base)); dx=self._margin-self.horizontalScrollBar().value(); dy=self._margin-self.verticalScrollBar().value()
        for rect in self.selectionRectangles():
            p.fillRect(rect.translated(dx,dy),self.palette().color(QPalette.ColorRole.Highlight))
        text_color=self.palette().color(QPalette.ColorRole.Text)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(text_color)
        for r in m.runs:
            painted_bounds=QRectF(r.x+dx,r.baseline-r.ascent+dy,r.advance,r.ascent+r.descent)
            if not painted_bounds.intersects(dirty_f):
                continue
            r.glyph_run.paint(p,QPointF(r.x+dx,r.baseline+dy))
        if self.hasFocus() and not self._read_only:p.fillRect(QRectF(self.cursorRect()),self.palette().color(QPalette.ColorRole.Text))
        p.end()
    def createStandardContextMenu(self):
        menu=QMenu(self)
        copy_action=menu.addAction("Copy"); copy_action.setShortcut(QKeySequence.StandardKey.Copy); copy_action.setEnabled(self.textCursor().hasSelection()); copy_action.triggered.connect(self.copy)
        paste_action=menu.addAction("Paste"); paste_action.setShortcut(QKeySequence.StandardKey.Paste); paste_action.setEnabled(not self._read_only); paste_action.triggered.connect(self.paste)
        select_all_action=menu.addAction("Select All"); select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll); select_all_action.triggered.connect(self.selectAll)
        return menu
    def contextMenuEvent(self,e):
        menu=self.createStandardContextMenu(); menu.exec(e.globalPos())
    def mouseDoubleClickEvent(self,e):
        if e.button()==Qt.MouseButton.LeftButton:
            text=self._text
            qt_position=self._hit_test(e.position())
            py_position=self._qt_to_py[qt_position]
            if py_position==len(text) and py_position:py_position-=1
            if py_position<len(text):
                def word_character(character):return character.isalnum() or character=="_" or unicodedata.category(character).startswith("M")
                start=py_position; end=py_position+1
                if word_character(text[py_position]):
                    while start>0 and word_character(text[start-1]):start-=1
                    while end<len(text) and word_character(text[end]):end+=1
                boundaries=_qt_boundaries(text)
                self._cursor_anchor=boundaries[start]; self._cursor_position=boundaries[end]
            else:self._cursor_anchor=0; self._cursor_position=0
            self.setFocus(); self.viewport().update(); e.accept(); return
        super().mouseDoubleClickEvent(e)
    def mousePressEvent(self,e):
        if e.button()==Qt.MouseButton.LeftButton:self._cursor_position=self._hit_test(e.position());self._cursor_anchor=self._cursor_position;self.setFocus();self.viewport().update()
        super().mousePressEvent(e)
    def mouseMoveEvent(self,e):
        if e.buttons()&Qt.MouseButton.LeftButton:self._cursor_position=self._hit_test(e.position());self.viewport().update()
        super().mouseMoveEvent(e)
    def keyPressEvent(self,e):
        if e.matches(QKeySequence.StandardKey.SelectAll):self.selectAll();return
        if e.matches(QKeySequence.StandardKey.Copy):self.copy();return
        if e.matches(QKeySequence.StandardKey.Cut):self.cut();return
        if e.matches(QKeySequence.StandardKey.Paste):self.paste();return
        if e.key()==Qt.Key.Key_Tab and self._tab_changes_focus:self.focusNextChild();return
        if self._read_only:super().keyPressEvent(e);return
        c=self.textCursor(); keep=QTextCursor.MoveMode.KeepAnchor if e.modifiers()&Qt.KeyboardModifier.ShiftModifier else QTextCursor.MoveMode.MoveAnchor
        if e.key()==Qt.Key.Key_Left:c.movePosition(QTextCursor.MoveOperation.Left,keep)
        elif e.key()==Qt.Key.Key_Right:c.movePosition(QTextCursor.MoveOperation.Right,keep)
        elif e.key()==Qt.Key.Key_Home:c.movePosition(QTextCursor.MoveOperation.Start,keep)
        elif e.key()==Qt.Key.Key_End:c.movePosition(QTextCursor.MoveOperation.End,keep)
        elif e.key()==Qt.Key.Key_Backspace:
            if not c.hasSelection():c.movePosition(QTextCursor.MoveOperation.Left,QTextCursor.MoveMode.KeepAnchor)
            self._replace_selection(c,'')
        elif e.key()==Qt.Key.Key_Delete:
            if not c.hasSelection():c.movePosition(QTextCursor.MoveOperation.Right,QTextCursor.MoveMode.KeepAnchor)
            self._replace_selection(c,'')
        elif e.key() in (Qt.Key.Key_Return,Qt.Key.Key_Enter):self._replace_selection(c,'\n')
        elif e.text() and not(e.modifiers()&(Qt.KeyboardModifier.ControlModifier|Qt.KeyboardModifier.MetaModifier)):self._replace_selection(c,e.text())
        else:super().keyPressEvent(e);return
        self.setTextCursor(c)
    def sizeHint(self):
        return QSize(160,48)

@lru_cache(maxsize=256)
def _pdf_font_family(font_file: Path) -> str:
    font_id = QFontDatabase.addApplicationFont(str(font_file))
    if font_id < 0:
        raise RuntimeError(f"PDF export could not register authored font: {font_file}")
    families = QFontDatabase.applicationFontFamilies(font_id)
    if not families:
        raise RuntimeError(f"PDF export font has no registered family: {font_file}")
    return families[0]


def _paint_pdf_text_run(painter: QPainter, run: ExactPlacedRun, origin: QPointF) -> None:
    font = QFont(_pdf_font_family(run.font_file))
    font.setPixelSize(max(1, int(round(run.glyph_run.pixel_size))))
    painter.setFont(font)
    painter.drawText(origin, run.text)


def _paint_exact_surface_slice(painter, surface: ExactFontTextEdit, model: ExactLayoutModel, page_top: float, page_height: float, x_offset: float = 0.0) -> None:
    margin = surface.documentMargin()
    painter.save()
    painter.translate(x_offset + margin, margin - page_top)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setPen(surface.palette().color(QPalette.ColorRole.Text))
    content_top = page_top - margin
    content_bottom = page_top + page_height - margin
    for run in model.runs:
        run_top = run.baseline - run.ascent
        run_bottom = run.baseline + run.descent
        if run_bottom < content_top or run_top > content_bottom:
            continue
        _paint_pdf_text_run(painter, run, QPointF(run.x, run.baseline))
    painter.restore()


def write_exact_surface_groups_pdf(
    groups: tuple[tuple[ExactFontTextEdit, ...], ...],
    path: str | Path,
    *,
    section_headers: tuple[str, ...] | None = None,
) -> Path:
    """Write exact-render surfaces to one PDF, optionally framed by exact section headers."""
    if not groups or any(not group for group in groups):
        raise ValueError("PDF export requires at least one rendered surface group")
    if section_headers is not None and len(section_headers) != len(groups):
        raise ValueError("PDF section-header count must equal rendered group count")
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    writer = QPdfWriter(str(destination))
    resolution = max(72, int(round(groups[0][0].logicalDpiY())))
    writer.setResolution(resolution)
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.Letter))
    writer.setPageMargins(QMarginsF(36.0, 36.0, 36.0, 36.0), QPageLayout.Unit.Point)
    painter = QPainter(writer)
    if not painter.isActive():
        raise RuntimeError(f"could not open PDF for writing: {destination}")
    first_page = True
    try:
        page_rect = writer.pageLayout().paintRectPixels(writer.resolution())
        for group_index, group in enumerate(groups):
            models = tuple(surface.exactLayoutModel() for surface in group)
            widths = tuple(max(1.0, float(surface.viewport().width()), model.width + surface.documentMargin() * 2) for surface, model in zip(group, models))
            heights = tuple(max(1.0, model.height + surface.documentMargin() * 2) for surface, model in zip(group, models))
            source_width = sum(widths)
            scale = page_rect.width() / source_width
            source_page_height = page_rect.height() / scale
            header_model = None
            header_height = 0.0
            if section_headers is not None:
                header_text = section_headers[group_index]
                header_sources = []
                qt_start = 0
                for character in header_text:
                    font_file = (
                        group[0].defaultFontFile()
                        if character == "\n"
                        else system_font_file_for_codepoint(ord(character))
                    )
                    header_sources.append(ExactSourceRun(qt_start, character, font_file, True))
                    qt_start += qt_utf16_units(character)
                header_layout = ExactHarfBuzzLayout(group[0]._pixel_size())
                try:
                    margin = group[0].documentMargin()
                    header_model = header_layout.layout(
                        header_text, tuple(header_sources), max(1.0, source_width - margin * 2), True
                    )
                finally:
                    header_layout.close()
                header_height = header_model.height + margin * 2
                if header_height >= source_page_height:
                    raise ValueError("PDF section header exceeds one export page")
            page_top = 0.0
            group_height = max(heights)
            first_section_page = True
            while page_top < group_height:
                if not first_page:
                    writer.newPage()
                first_page = False
                painter.fillRect(QRectF(page_rect), group[0].palette().color(QPalette.ColorRole.Base))
                painter.save()
                painter.translate(page_rect.left(), page_rect.top())
                painter.scale(scale, scale)
                content_offset = header_height if first_section_page else 0.0
                available_height = source_page_height - content_offset
                if first_section_page and header_model is not None:
                    margin = group[0].documentMargin()
                    painter.save()
                    painter.translate(margin, margin)
                    painter.setPen(group[0].palette().color(QPalette.ColorRole.Text))
                    for run in header_model.runs:
                        _paint_pdf_text_run(painter, run, QPointF(run.x, run.baseline))
                    painter.restore()
                    painter.translate(0.0, content_offset)
                x_offset = 0.0
                for surface, model, width in zip(group, models, widths):
                    _paint_exact_surface_slice(painter, surface, model, page_top, available_height, x_offset)
                    x_offset += width
                painter.restore()
                page_top += available_height
                first_section_page = False
    finally:
        painter.end()
    return destination


def write_exact_surface_pdf(surface: ExactFontTextEdit, path: str | Path) -> Path:
    """Write one existing exact-render surface to a paginated PDF."""
    return write_exact_surface_groups_pdf(((surface,),), path)


def exact_grimchain_text_extent(text:str,point_size:float)->QSizeF:
    if point_size<=0:raise ValueError('GrimChain metric point size must be positive')
    if not text:return QSizeF(0,0)
    screen=QGuiApplication.primaryScreen();dpi=96.0 if screen is None else float(screen.logicalDotsPerInchY());px=point_size*dpi/72.0;width=0.0;height=0.0
    for ch in text:
        face=grimchain_face_for_character(ch);_r,a,d,adv=_shape_exact_font(face.file,ch,px);width+=adv;height=max(height,a+d)
    return QSizeF(width,height)

def _require_exact_surface(widget):
    if not isinstance(widget,ExactFontTextEdit):raise TypeError('authored font rendering requires ExactFontTextEdit')
    return widget

def format_exact_grimchain(widget,text=None):
    s=_require_exact_surface(widget)
    if s.property('_exact_font_formatting'):return
    s.setProperty('_exact_font_formatting',True)
    try:
        text=s.toPlainText() if text is None else text
        if text!=s.toPlainText():raise ValueError('GrimChain formatter text must match the widget text')
        s.clear_exact_spans();q=0
        for ch in text:
            units=2 if ord(ch)>0xFFFF else 1
            f=grimchain_face_for_character(ch)
            s.add_exact_font_span(q,ch,f.family,f.file)
            q+=units
    finally:s.setProperty('_exact_font_formatting',False)

def format_exact_grimchain_span(widget,qt_start,text):
    s=_require_exact_surface(widget);off=qt_start
    for ch in text:
        f=grimchain_face_for_character(ch);s.add_exact_font_span(off,ch,f.family,f.file);off+=2 if ord(ch)>0xFFFF else 1

def format_definition_grimchains(widget,text):
    s=_require_exact_surface(widget)
    if text!=s.toPlainText():raise ValueError('Definition formatter text must match the widget text')
    offset=0;prefix='GrimChain: '
    for line in text.splitlines(keepends=True):
        body=line[:-1] if line.endswith('\n') else line
        if body.startswith(prefix):
            value=body[len(prefix):]
            if value:format_exact_grimchain_span(s,qt_utf16_units(text[:offset+len(prefix)]),value)
        offset+=len(line)
