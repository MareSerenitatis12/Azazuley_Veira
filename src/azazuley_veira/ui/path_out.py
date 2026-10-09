"""Dynamic, isolated Path Out tree. Geometry follows the recorded relations."""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QAction, QColor, QPainter, QPainterPath, QPalette, QPen
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QFrame, QGraphicsScene, QGraphicsView, QHBoxLayout,
    QLabel, QPushButton, QVBoxLayout, QWidget,
)

from azazuley_veira.config.font_runtime import grimchain_face_for_character
from azazuley_veira.ui.exact_text import _glyph_path, _shape_exact_font


class _GlyphBody(QWidget):
    """Paint projected traversal left to right, using existing physical faces.

    Shape each source glyph independently so natural bidi cannot reorder an
    already traversed body a second time. No font resources are modified.
    """

    def __init__(self, text, width, parent=None):
        super().__init__(parent)
        self.text = text
        self.runs = []
        shaped = []
        max_ascent, max_descent = 0.0, 0.0
        i = 0
        while i < len(text):
            character = text[i]
            i += 1
            if character.isspace():
                shaped.append((character, None, 0.0, None))
                continue
            glyph = character
            while i < len(text) and text[i] == '\ufe0e':
                glyph += text[i]
                i += 1
            face = grimchain_face_for_character(character)
            run, ascent, descent, advance = _shape_exact_font(face.file, glyph, 18.0)
            # Use the visible outlines, rather than a font's full ascender/
            # descender range, to avoid oversized gaps between glyph lines.
            scale = run.pixel_size / run.upem
            ascent, descent = 0.0, 0.0
            for glyph_id, offset in zip(run.glyph_indexes, run.positions):
                bounds = _glyph_path(face.file, glyph_id).boundingRect()
                ascent = max(ascent, bounds.bottom() * scale - offset.y())
                descent = max(descent, -bounds.top() * scale + offset.y())
            max_ascent = max(max_ascent, ascent)
            max_descent = max(max_descent, descent)
            shaped.append((glyph, run, advance, face.file))
        self.line_height = max(24, math.ceil(max_ascent + max_descent) + 4)
        x, y = 0.0, 0.0
        for glyph, run, advance, font_file in shaped:
            if glyph == '\n':
                x, y = 0.0, y + self.line_height
                continue
            if run is None:
                x += 7.0
                continue
            if x + advance > width and x:
                x, y = 0.0, y + self.line_height
            self.runs.append((run, QPointF(x, y + max_ascent + 2), font_file))
            x += advance + 2.0
        self.setFixedSize(width, math.ceil(y + self.line_height))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.palette().windowText())
        for run, origin, _font_file in self.runs:
            run.paint(painter, origin)


class PathOutView(QWidget):
    """Lazy tree surface with pan, bounded zoom, and legible reset."""

    def __init__(self, parent=None, *, reverse=False, for_export=False):
        super().__init__(parent)
        self.reverse = reverse
        self.for_export = for_export
        self.path_name = 'Path Back' if reverse else 'Path Out'
        self.model = None
        self._dirty = False
        self.cards = []
        self.rows = []
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.status = QLabel(f'Translate a GrimChain to see its {self.path_name}.')
        tools = QHBoxLayout()
        tools.addWidget(self.status, 1)
        self.details_toggle = QCheckBox('More detail')
        self.details_toggle.toggled.connect(self._set_details)
        tools.addWidget(self.details_toggle)
        for label, callback in (
            ('−', lambda: self.zoom(1 / 1.2)),
            ('+', lambda: self.zoom(1.2)),
            ('Fit tree', self.fit_tree),
            ('Actual size', self.actual_size),
        ):
            button = QPushButton(label)
            button.clicked.connect(callback)
            tools.addWidget(button)
        layout = QVBoxLayout(self)
        layout.addLayout(tools)
        layout.addWidget(self.view, 1)

    def set_path(self, model):
        self.model = model
        self._dirty = True
        self.scene.clear()
        self.cards = []
        self.rows = []
        if model is None:
            self.status.setText(f'Translate a GrimChain to see its {self.path_name}.')
        elif model.capture_error:
            self.status.setText(self.path_name + ' capture failed: ' + model.capture_error)
        else:
            self.status.setText(f'{len(model.steps)} transformations · drag to pan')
        if self.isVisible():
            self._draw()

    def showEvent(self, event):
        super().showEvent(event)
        if self._dirty:
            self._draw()

    def zoom(self, factor):
        scale = self.view.transform().m11() * factor
        if 0.08 <= scale <= 4:
            self.view.scale(factor, factor)

    def fit_tree(self):
        if self.scene.items():
            self.view.fitInView(self.scene.itemsBoundingRect().adjusted(-30, -30, 30, 30), Qt.AspectRatioMode.KeepAspectRatio)

    def actual_size(self):
        self.view.resetTransform()
        self.view.centerOn(0, self.view.viewport().height() / 2 - 20)

    def _set_details(self, checked):
        self._dirty = True
        if self.isVisible():
            self._draw()

    def _card(self, title, glyphs, detail, center, y, width=540, *, explain=False, offices=()):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setAutoFillBackground(True)
        if self.for_export:
            palette = card.palette()
            palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
            card.setPalette(palette)
        font = card.font()
        font.setPointSizeF(9)
        card.setFont(font)
        card.setToolTip(detail)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(2)
        heading = QLabel(title)
        heading.setWordWrap(True)
        font = heading.font()
        font.setBold(True)
        heading.setFont(font)
        layout.addWidget(heading)
        if glyphs:
            body = _GlyphBody(glyphs, width - 12)
            body.setToolTip(detail)
            layout.addWidget(body)
        if offices:
            names = offices[0] if len(offices) == 1 else ', '.join(offices[:-1]) + ' and ' + offices[-1]
            inheritance = QLabel('Uttered as ' + names + '.')
            inheritance.setTextFormat(Qt.TextFormat.PlainText)
            inheritance.setWordWrap(True)
            layout.addWidget(inheritance)
        if self.details_toggle.isChecked() or explain:
            description = QLabel(detail)
            description.setTextFormat(Qt.TextFormat.PlainText)
            description.setWordWrap(True)
            description.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            layout.addWidget(description)
        if glyphs and not self.for_export:
            copy = QAction('Copy glyph body', card)
            copy.triggered.connect(lambda: QApplication.clipboard().setText(glyphs))
            card.addAction(copy)
            card.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        card.setFixedWidth(width)
        card.adjustSize()
        proxy = self.scene.addWidget(card)
        proxy.setPos(center - width / 2, y)
        self.cards.append((title, glyphs, proxy))
        return proxy

    def _edge(self, first, second):
        start = first.sceneBoundingRect().bottomLeft()
        start.setX(first.sceneBoundingRect().center().x())
        end = second.sceneBoundingRect().topLeft()
        end.setX(second.sceneBoundingRect().center().x())
        path = QPainterPath(start)
        middle = (start.y() + end.y()) / 2
        path.cubicTo(QPointF(start.x(), middle), QPointF(end.x(), middle), end)
        item = self.scene.addPath(path, QPen(QColor('#708b99'), 2))
        item.setZValue(-1)
        self.scene.addLine(end.x() - 5, end.y() - 8, end.x(), end.y(), QPen(QColor('#708b99'), 2)).setZValue(-1)
        self.scene.addLine(end.x() + 5, end.y() - 8, end.x(), end.y(), QPen(QColor('#708b99'), 2)).setZValue(-1)

    def _draw(self):
        self._dirty = False
        self.scene.clear()
        self.cards = []
        self.rows = []
        if self.model is None or self.model.capture_error:
            return
        try:
            model = self.model
            start_title = 'Transformed GrimChain' if self.reverse else 'Original GrimChain'
            start_body = model.final_body if self.reverse else model.source
            previous = self._card(start_title, start_body, 'The complete GrimChain.', 0, 0)
            self._row(previous)
            y = previous.sceneBoundingRect().bottom() + 18
            steps = reversed(tuple(enumerate(model.steps, 1))) if self.reverse else enumerate(model.steps, 1)
            for index, step in steps:
                label = f'{index} · {step.label}' + (' · back' if self.reverse else '')
                explanation = ('Restore the complete chain from before this ' + step.label + ' transformation.') if self.reverse else step.explanation
                operator = self._card(label, step.operators, explanation, -170, y, 260, explain=True)
                targets = self._card('Affected body', step.after_targets if self.reverse else step.targets, 'The glyphs affected by this Enochian.', 170, y, 260,
                                     offices=step.offices)
                self._row(operator, targets)
                self._edge(previous, operator)
                self._edge(previous, targets)
                y = max(operator.sceneBoundingRect().bottom(), targets.sceneBoundingRect().bottom()) + 12
                title = 'Previous GrimChain' if self.reverse else 'GrimChain after transformation'
                body = step.before_body if self.reverse else step.body
                node = self._card(title, body, explanation, 0, y)
                self._row(node)
                self._edge(operator, node)
                self._edge(targets, node)
                previous = node
                y = node.sceneBoundingRect().bottom() + 18
            title = 'Original GrimChain' if self.reverse else 'Transformed GrimChain'
            body = model.source if self.reverse else model.final_body
            detail = 'The original written chain.' if self.reverse else 'The complete chain after its Enochian transformations.'
            if not model.steps:
                detail = 'No Enochian transformation moves this chain; it remains as written.'
            node = self._card(title, body, detail, 0, y, explain=True)
            self._row(node)
            self._edge(previous, node)
            self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-40, -40, 40, 40))
            self.view.resetTransform()
            self.view.centerOn(0, self.view.viewport().height() / 2 - 20)
        except Exception as exc:
            self.scene.clear()
            self.cards = []
            self.rows = []
            self.status.setText(f'{self.path_name} could not be displayed: {exc}')

    def _row(self, *nodes):
        self.rows.append((min(node.sceneBoundingRect().top() for node in nodes), max(node.sceneBoundingRect().bottom() for node in nodes)))


class PathBackView(PathOutView):
    """Walk the stored forward witness backward, without translating again."""

    def __init__(self, parent=None):
        super().__init__(parent, reverse=True)
