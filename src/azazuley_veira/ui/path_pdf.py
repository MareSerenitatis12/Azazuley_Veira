"""Paginated vector export of the same compact forward/reverse path tree."""
from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtCore import QMarginsF, QPoint, QRectF, Qt
from PySide6.QtGui import QFont, QPageLayout, QPageSize, QPainter, QPdfWriter

from azazuley_veira.ui.path_out import PathOutView, _GlyphBody


def _page_end(view, top, limit):
    # Keep ordinary rows together. Oversized glyph cards continue on the next
    # page at a whole glyph-line boundary, never shrinking an entire tall tree.
    complete = [bottom + 6 for row_top, bottom in view.rows if row_top >= top and bottom + 6 <= limit]
    if complete:
        return max(complete)
    for _title, _glyphs, proxy in view.cards:
        for body in proxy.widget().findChildren(_GlyphBody):
            start = proxy.pos().y() + body.mapTo(proxy.widget(), QPoint(0, 0)).y()
            if start < limit < start + body.height():
                cut = start + math.floor((limit - start) / body.line_height) * body.line_height
                if cut > top:
                    return cut
    return limit


def write_path_pdf(model, path: str | Path, *, reverse=False) -> Path:
    """Export all recorded nodes independently of tab visibility or zoom."""
    if model is None:
        raise ValueError('Render a GrimChain before exporting its path')
    if model.capture_error:
        raise ValueError('Cannot export an incomplete path: ' + model.capture_error)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + '.tmp')
    view = PathOutView(reverse=reverse, for_export=True)
    painter = QPainter()
    try:
        view.set_path(model)
        view._draw()
        if not view.cards:
            raise RuntimeError(view.status.text())
        bounds = view.scene.itemsBoundingRect().adjusted(-10, -8, 10, 8)
        writer = QPdfWriter(str(temporary))
        writer.setTitle(view.path_name)
        writer.setCreator('Azazuley Veira Language Terminal')
        writer.setResolution(96)
        writer.setPageSize(QPageSize(QPageSize.PageSizeId.Letter))
        writer.setPageMargins(QMarginsF(36, 36, 36, 36), QPageLayout.Unit.Point)
        if not painter.begin(writer):
            raise RuntimeError('Could not open path PDF for writing')
        width, height = float(writer.width()), float(writer.height())
        header, footer = 32.0, 28.0
        scale = min(1.0, width / bounds.width())
        available = (height - header - footer) / scale
        top, page = bounds.top(), 1
        while top < bounds.bottom():
            limit = min(top + available, bounds.bottom())
            bottom = limit if limit == bounds.bottom() else _page_end(view, top, limit)
            if bottom <= top:
                raise RuntimeError('Path PDF pagination made no progress')
            if page > 1 and not writer.newPage():
                raise RuntimeError('Could not append path PDF page')
            painter.resetTransform()
            painter.setClipping(False)
            painter.fillRect(QRectF(0, 0, width, height), Qt.GlobalColor.white)
            target = QRectF((width - bounds.width() * scale) / 2, header, bounds.width() * scale, (bottom - top) * scale)
            painter.save()
            painter.setClipRect(target)
            view.scene.render(painter, target, QRectF(bounds.left(), top, bounds.width(), bottom - top))
            painter.restore()
            # Proxy widgets can paint their backgrounds during scene export.
            # Paint page furniture last so continuation cards cannot cover it.
            painter.resetTransform()
            painter.setClipping(False)
            painter.fillRect(QRectF(0, 0, width, header), Qt.GlobalColor.white)
            painter.fillRect(QRectF(0, height - footer, width, footer), Qt.GlobalColor.white)
            painter.setPen(Qt.GlobalColor.black)
            font = QFont()
            font.setPointSizeF(11)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(QRectF(0, 0, width, header), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, view.path_name)
            font.setPointSizeF(8)
            font.setBold(False)
            painter.setFont(font)
            suffix = ' - continues' if bottom < bounds.bottom() else ''
            painter.drawText(QRectF(0, height - footer, width, footer), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f'{view.path_name} - page {page}{suffix}')
            top, page = bottom, page + 1
        painter.end()
        temporary.replace(destination)
        return destination
    except Exception:
        if painter.isActive():
            painter.end()
        temporary.unlink(missing_ok=True)
        raise
    finally:
        view.deleteLater()
