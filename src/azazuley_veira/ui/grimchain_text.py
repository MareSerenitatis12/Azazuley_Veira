from __future__ import annotations

from PySide6.QtCore import QSizeF
from PySide6.QtGui import QFontMetricsF, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit

from azazuley_veira.config.font_runtime import exact_grimchain_font, grimchain_face_map, grimchain_face_runs


def qt_utf16_units(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def exact_grimchain_text_extent(text: str, point_size: float) -> QSizeF:
    if point_size <= 0:
        raise ValueError("GrimChain metric point size must be positive")
    if not text:
        return QSizeF(0.0, 0.0)
    width = 0.0
    height = 0.0
    for start, end, _face in grimchain_face_runs(text):
        run_text = text[start:end]
        metrics = QFontMetricsF(exact_grimchain_font(run_text[0], point_size))
        width += metrics.horizontalAdvance(run_text)
        height = max(height, metrics.height())
    return QSizeF(width, height)


def _apply_range(widget: QPlainTextEdit, text: str, start: int, end: int) -> None:
    if start < 0 or end < start or end > len(text):
        raise ValueError((start, end, len(text)))
    body = text[start:end]
    if not body:
        return
    point_size = widget.font().pointSizeF()
    for run_start, run_end, _face in grimchain_face_runs(body):
        prefix_start = start + run_start
        prefix_end = start + run_end
        cursor = QTextCursor(widget.document())
        cursor.setPosition(qt_utf16_units(text[:prefix_start]))
        cursor.setPosition(qt_utf16_units(text[:prefix_end]), QTextCursor.MoveMode.KeepAnchor)
        fmt = QTextCharFormat()
        fmt.setFont(exact_grimchain_font(body[run_start], point_size))
        cursor.mergeCharFormat(fmt)


def format_exact_grimchain(widget: QPlainTextEdit, text: str | None = None) -> None:
    if widget.property("_grimchain_formatting"):
        return
    widget.setProperty("_grimchain_formatting", True)
    try:
        if text is None:
            text = widget.toPlainText()
        if text != widget.toPlainText():
            raise ValueError("GrimChain formatter text must match the widget document")
        original = widget.textCursor()
        position, anchor = original.position(), original.anchor()
        known = grimchain_face_map()
        start: int | None = None
        for index, character in enumerate(text):
            if ord(character) in known:
                if start is None:
                    start = index
            elif start is not None:
                _apply_range(widget, text, start, index)
                start = None
        if start is not None:
            _apply_range(widget, text, start, len(text))
        restored = widget.textCursor()
        restored.setPosition(anchor)
        restored.setPosition(position, QTextCursor.MoveMode.KeepAnchor)
        widget.setTextCursor(restored)
    finally:
        widget.setProperty("_grimchain_formatting", False)


def format_exact_grimchain_span(widget: QPlainTextEdit, qt_start: int, text: str) -> None:
    if not text:
        return
    point_size = widget.font().pointSizeF()
    for run_start, run_end, _face in grimchain_face_runs(text):
        start = qt_start + qt_utf16_units(text[:run_start])
        end = qt_start + qt_utf16_units(text[:run_end])
        cursor = QTextCursor(widget.document())
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        if cursor.selectedText().replace("\u2029", "\n") != text[run_start:run_end]:
            raise ValueError("GrimChain presentation span text/provenance mismatch")
        fmt = QTextCharFormat()
        fmt.setFont(exact_grimchain_font(text[run_start], point_size))
        cursor.mergeCharFormat(fmt)


def format_definition_grimchains(widget: QPlainTextEdit, text: str) -> None:
    if text != widget.toPlainText():
        raise ValueError("Definition formatter text must match the widget document")
    offset = 0
    prefix = "GrimChain: "
    for line in text.splitlines(keepends=True):
        body = line[:-1] if line.endswith("\n") else line
        if body.startswith(prefix):
            start = offset + len(prefix)
            end = offset + len(body)
            if end > start:
                _apply_range(widget, text, start, end)
        offset += len(line)
