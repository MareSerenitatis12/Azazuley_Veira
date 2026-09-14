from __future__ import annotations

import unicodedata

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QKeyEvent, QPalette
from azazuley_veira.ailalubar_render import AilalubarReflection, AilalubarRenderWitness
from azazuley_veira.config.font_runtime import (
    authored_lexical_font_file,
    grimchain_display_codepoints,
    grimchain_face_for_character,
    physical_font_family,
    system_font_file_for_codepoint,
    system_font_file_for_family,
)
from azazuley_veira.engines.sydonic import (
    BREATH_SEPARATOR,
    OSTENSIVE_PARAGRAPH_PREFIXES,
    DefinitionPresentation,
    LeySyffPresentation,
    PresentationSpan,
)
from azazuley_veira.ui.exact_text import (
    ExactFontTextEdit,
    format_definition_grimchains,
    format_exact_grimchain,
    format_exact_grimchain_span,
    qt_utf16_units,
)

from sydonic_magicae_translation_matrix.canon_dictionary import read_canon_dictionary

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollBar,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


def _format_exact_prose_uncovered(widget: ExactFontTextEdit) -> None:
    """Resolve every uncovered prose code point through the host font system."""
    text = widget.toPlainText()
    grimchain_codepoints = grimchain_display_codepoints()
    spans = widget.exact_spans()
    span_index = 0
    qt_start = 0
    group_start: int | None = None
    group_text = ""
    group_file = None

    def flush() -> None:
        nonlocal group_start, group_text, group_file
        if group_start is not None and group_text and group_file is not None:
            widget.add_exact_font_span(
                group_start,
                group_text,
                physical_font_family(group_file),
                group_file,
            )
        group_start = None
        group_text = ""
        group_file = None

    for character in text:
        units = qt_utf16_units(character)
        while span_index < len(spans) and spans[span_index].qt_end <= qt_start:
            span_index += 1
        covered = (
            span_index < len(spans)
            and spans[span_index].qt_start <= qt_start < spans[span_index].qt_end
        )
        if character == "\n" or covered:
            flush()
            qt_start += units
            continue

        if ord(character) in grimchain_codepoints:
            exact_file = grimchain_face_for_character(character).file
        else:
            exact_file = system_font_file_for_codepoint(ord(character))

        if group_file is not None and exact_file != group_file:
            flush()
        if group_start is None:
            group_start = qt_start
            group_file = exact_file
        group_text += character
        qt_start += units
    flush()


def _format_ostensive_paragraph_markers(widget: ExactFontTextEdit) -> None:
    """Paint RTL paragraph markers through the existing exact system-codepoint authority."""
    text = widget.toPlainText()
    qt_start = 0
    for character in text:
        if character in OSTENSIVE_PARAGRAPH_PREFIXES:
            font_file = system_font_file_for_codepoint(ord(character))
            widget.add_exact_font_span(
                qt_start, character, physical_font_family(font_file), font_file
            )
        qt_start += qt_utf16_units(character)


class SubmitTextEdit(ExactFontTextEdit):
    submitted = Signal(str)

    def __init__(self, parent=None, preferred_rows: int = 3):
        super().__init__(parent)
        self._preferred_rows = preferred_rows

    def sizeHint(self) -> QSize:
        base = super().sizeHint()
        line_height = self.defaultLineHeight()
        document_margin = float(self.documentMargin()) * 2.0
        frame = float(self.frameWidth()) * 2.0
        margins = self.viewportMargins()
        height = line_height * self._preferred_rows + document_margin + frame + margins.top() + margins.bottom()
        return QSize(base.width(), round(height))

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.submitted.emit(self.toPlainText())
            return
        super().keyPressEvent(event)




class SingleLineGrimChainEdit(ExactFontTextEdit):
    """Read-only single-line document surface with mixed exact GrimChain faces."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(ExactFontTextEdit.LineWrapMode.NoWrap)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def setText(self, value: str) -> None:
        self.setPlainText(value)
        format_exact_grimchain(self, value)

    def text(self) -> str:
        return self.toPlainText()

    def setAlignment(self, alignment: Qt.AlignmentFlag) -> None:
        super().setAlignment(alignment)


class Terminal(QWidget):
    user_song_submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        self.user_song = SubmitTextEdit()
        self.user_song.setObjectName("userSong")
        self._frame_field(self.user_song)
        self.user_song.setLineWrapMode(ExactFontTextEdit.LineWrapMode.WidgetWidth)
        self.user_song.setTabChangesFocus(True)
        self.user_song.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.user_song.submitted.connect(self.user_song_submitted)
        self.user_header = QHBoxLayout()
        self.user_header.addWidget(self._label("Et Sonyera>"))
        self.user_header.addStretch(1)
        layout.addLayout(self.user_header)
        layout.addWidget(self.user_song)

        daemon_header = QHBoxLayout()
        daemon_header.setSpacing(12)
        daemon_header.addWidget(self._label("Domus House>"))
        daemon_header.addStretch(1)
        layout.addLayout(daemon_header)

        daemon_row = QHBoxLayout()
        daemon_row.setSpacing(0)
        self.daemon_first = self._daemon_part()
        self.daemon_middle = self._daemon_middle_part()
        self.daemon_middle_second = self._daemon_middle_part()
        self.daemon_second = self._daemon_part()
        domus_field_width = 244
        domus_field_height = 44
        for field in (
            self.daemon_first,
            self.daemon_middle,
            self.daemon_middle_second,
            self.daemon_second,
        ):
            field.setFixedSize(domus_field_width, domus_field_height)

        left_group = QWidget()
        left_group_layout = QHBoxLayout(left_group)
        left_group_layout.setContentsMargins(0, 0, 0, 0)
        left_group_layout.setSpacing(0)
        left_group_layout.addWidget(self.daemon_first)

        center_stack = QWidget()
        center_stack_layout = QVBoxLayout(center_stack)
        center_stack_layout.setContentsMargins(0, 0, 0, 0)
        center_stack_layout.setSpacing(6)
        center_stack_layout.addWidget(self.daemon_middle)
        center_stack_layout.addWidget(self.daemon_middle_second)

        right_group = QWidget()
        right_group_layout = QHBoxLayout(right_group)
        right_group_layout.setContentsMargins(0, 0, 0, 0)
        right_group_layout.setSpacing(0)
        right_group_layout.addWidget(self.daemon_second)

        daemon_row.addStretch(1)
        daemon_row.addWidget(left_group, 0, Qt.AlignmentFlag.AlignVCenter)
        daemon_row.addSpacing(10)
        daemon_row.addWidget(center_stack, 0, Qt.AlignmentFlag.AlignVCenter)
        daemon_row.addSpacing(10)
        daemon_row.addWidget(right_group, 0, Qt.AlignmentFlag.AlignVCenter)
        daemon_row.addStretch(1)
        layout.addLayout(daemon_row)

        self.output_tabs = QTabWidget()
        self.output_tabs.setObjectName("outputTabs")

        self.utterance_output = self._output_field()
        self.ailalubar_output = self._output_field()
        self.azazuley_output = self._output_field()
        self.ailalaza_output = self._output_field()
        self.definition_output = self._output_field()
        self.canon_glossary_output = self._output_field()
        self.leysyff_output = self._output_field()
        self.ffysyel_output = self._output_field()
        self.glossolalia_output = self._output_field()
        self.ailalossolg_output = self._output_field()

        self.leysyff_output.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ffysyel_output.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.leysyff_output.setFrameShape(QFrame.Shape.NoFrame)
        self.ffysyel_output.setFrameShape(QFrame.Shape.NoFrame)
        initial_palette = self.leysyff_output.palette()
        self._set_scripture_surface_colors(
            initial_palette.color(QPalette.ColorRole.Base).name(),
            initial_palette.color(QPalette.ColorRole.Text).name(),
        )

        self.leysyff_ffysyel_output = QWidget()
        self.leysyff_ffysyel_output.setObjectName("leysyffFfysyelOutput")
        scripture_layout = QHBoxLayout(self.leysyff_ffysyel_output)
        scripture_layout.setContentsMargins(0, 0, 0, 0)
        scripture_layout.setSpacing(0)
        scripture_layout.addWidget(self.leysyff_output, 1)
        scripture_layout.addWidget(self.ffysyel_output, 1)
        self.scripture_scrollbar = QScrollBar(Qt.Orientation.Vertical)
        self.scripture_scrollbar.setObjectName("scriptureScrollBar")
        scripture_layout.addWidget(self.scripture_scrollbar)
        self.scripture_scrollbar.valueChanged.connect(self._set_scripture_scroll_value)
        self.leysyff_output.verticalScrollBar().valueChanged.connect(
            self._sync_scripture_scroll_from_side
        )
        self.ffysyel_output.verticalScrollBar().valueChanged.connect(
            self._sync_scripture_scroll_from_side
        )

        self.output_tabs.addTab(self.utterance_output, "Rabulalia")
        self.output_tabs.addTab(self.ailalubar_output, "Ailalubar")
        self.output_tabs.addTab(self.azazuley_output, "Azalalia")
        self.output_tabs.addTab(self.ailalaza_output, "Ailalaza")
        self.output_tabs.addTab(self.glossolalia_output, "Glossolalia")
        self.output_tabs.addTab(self.ailalossolg_output, "Ailalossolg")
        self.output_tabs.addTab(self.leysyff_ffysyel_output, "LeySyff | FfysYel")
        self.output_tabs.addTab(self.definition_output, "Definition")
        self.output_tabs.addTab(self.canon_glossary_output, "Canon Glossary")
        self.output_tabs.currentChanged.connect(self._refresh_scripture_tab_geometry)
        layout.addWidget(self.output_tabs, 1)

        prose_file = system_font_file_for_family("Noto Sans")
        self.user_song.setDefaultFontFile(prose_file)

        for field in (
            self.daemon_first,
            self.daemon_middle,
            self.daemon_middle_second,
            self.daemon_second,
            self.utterance_output,
            self.ailalubar_output,
            self.azazuley_output,
            self.ailalaza_output,
            self.leysyff_output,
            self.ffysyel_output,
            self.definition_output,
            self.canon_glossary_output,
            self.glossolalia_output,
            self.ailalossolg_output,
        ):
            field.setDefaultFontFile(prose_file)

        self.canon_glossary_output.setPlainText(read_canon_dictionary())
        _format_exact_prose_uncovered(self.canon_glossary_output)

        self._refresh_scripture_geometry()

    def set_user_font_selector(self, selector: QWidget) -> None:
        """Place the Et Sonyera font selector at the right edge of its label row."""
        self.user_header.addWidget(selector, 0, Qt.AlignmentFlag.AlignRight)

    def _daemon_part(self) -> SingleLineGrimChainEdit:
        field = SingleLineGrimChainEdit()
        field.setFrameShape(QFrame.Shape.NoFrame)
        field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return field

    def _daemon_middle_part(self) -> SingleLineGrimChainEdit:
        field = SingleLineGrimChainEdit()
        field.setFrameShape(QFrame.Shape.NoFrame)
        field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return field

    def _frame_field(self, field: ExactFontTextEdit) -> None:
        field.setFrameShape(QFrame.Shape.Box)
        field.setFrameShadow(QFrame.Shadow.Plain)
        field.setLineWidth(1)

    def _label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("fieldPrompt")
        return label

    def _output_field(self) -> ExactFontTextEdit:
        field = ExactFontTextEdit()
        field.setObjectName("resultField")
        self._frame_field(field)
        field.setReadOnly(True)
        field.setLineWrapMode(ExactFontTextEdit.LineWrapMode.WidgetWidth)
        field.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        field.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return field

    def _set_scripture_surface_colors(self, background: str, text: str) -> None:
        self.leysyff_output.setStyleSheet(
            f"border: 1px solid {text}; border-right-width: 0px; "
            f"background: {background}; color: {text};"
        )
        self.ffysyel_output.setStyleSheet(
            f"border: 1px solid {text}; background: {background}; color: {text};"
        )

    def _set_scripture_scroll_value(self, value: int) -> None:
        for field in (self.leysyff_output, self.ffysyel_output):
            bar = field.verticalScrollBar()
            if bar.value() != value:
                bar.setValue(value)

    def _sync_scripture_scroll_from_side(self, value: int) -> None:
        if self.scripture_scrollbar.value() != value:
            self.scripture_scrollbar.setValue(value)

    def _refresh_scripture_scroll_range(self) -> None:
        self.leysyff_output.exactLayoutModel()
        self.ffysyel_output.exactLayoutModel()
        left_bar = self.leysyff_output.verticalScrollBar()
        right_bar = self.ffysyel_output.verticalScrollBar()
        maximum = max(left_bar.maximum(), right_bar.maximum())
        viewport_height = max(1, min(
            self.leysyff_output.viewport().height(),
            self.ffysyel_output.viewport().height(),
        ))
        single_step = max(1, round(self.leysyff_output.defaultLineHeight()))
        current = min(self.scripture_scrollbar.value(), maximum)
        self.scripture_scrollbar.setRange(0, maximum)
        self.scripture_scrollbar.setPageStep(viewport_height)
        self.scripture_scrollbar.setSingleStep(single_step)
        self.scripture_scrollbar.setValue(current)
        self._set_scripture_scroll_value(current)

    def _refresh_scripture_tab_geometry(self, _index: int) -> None:
        if self.output_tabs.currentWidget() is self.leysyff_ffysyel_output:
            self._refresh_scripture_geometry()

    def _scripture_scroll_anchor(self) -> tuple[int, float] | None:
        if not (self.leysyff_output.scripturePageLayout() and self.ffysyel_output.scripturePageLayout()):
            return None
        page_height, page_gap = self.leysyff_output.scripturePageGeometry()
        if page_height <= 0:
            return None
        scroll_value = max(0.0, float(self.scripture_scrollbar.value()))
        stride = page_height + page_gap
        page_index = int(scroll_value // stride) if stride > 0 else 0
        page_top = page_index * stride
        fraction = max(0.0, min(1.0, (scroll_value - page_top) / page_height))
        return page_index, fraction

    def _restore_scripture_scroll_anchor(self, anchor: tuple[int, float] | None) -> None:
        if anchor is None:
            return
        page_height, page_gap = self.leysyff_output.scripturePageGeometry()
        if page_height <= 0:
            return
        page_index, fraction = anchor
        value = round(page_index * (page_height + page_gap) + page_height * fraction)
        self.scripture_scrollbar.setValue(min(value, self.scripture_scrollbar.maximum()))

    def _refresh_scripture_geometry(self) -> None:
        anchor = self._scripture_scroll_anchor()
        scrollbar_width = max(0.0, float(self.scripture_scrollbar.sizeHint().width()))
        spread_width = max(1.0, float(self.leysyff_ffysyel_output.width()) - scrollbar_width)
        viewport_height = max(1.0, float(min(
            self.leysyff_output.viewport().height(),
            self.ffysyel_output.viewport().height(),
        )))
        text_margin = max(4.0, spread_width * 0.025)
        vertical_margin = 8.0
        page_gap = 12.0
        point_size = max(8.0, min(14.0, spread_width * 0.0105))

        for field in (self.leysyff_output, self.ffysyel_output):
            field.setDocumentMargin(text_margin)
            field.setPointSizeF(point_size)

        required_height = max(
            self.leysyff_output.scriptureRequiredPageHeight(vertical_margin, vertical_margin),
            self.ffysyel_output.scriptureRequiredPageHeight(vertical_margin, vertical_margin),
        )
        page_height = max(viewport_height, required_height)

        for field in (self.leysyff_output, self.ffysyel_output):
            field.setScriptureMinimumPageCount(1)
            field.setScripturePageLayout(
                True,
                page_height=page_height,
                page_gap=page_gap,
                top_margin=vertical_margin,
                bottom_margin=vertical_margin,
            )

        shared_page_count = max(
            self.leysyff_output.scriptureContentPageCount(),
            self.ffysyel_output.scriptureContentPageCount(),
        )
        self.leysyff_output.setScriptureMinimumPageCount(shared_page_count)
        self.ffysyel_output.setScriptureMinimumPageCount(shared_page_count)
        self._refresh_scripture_scroll_range()
        self._restore_scripture_scroll_anchor(anchor)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, "leysyff_ffysyel_output"):
            self._refresh_scripture_geometry()

    def _content_widgets(self) -> tuple[QWidget, ...]:
        return (
            self.user_song,
            self.daemon_first,
            self.daemon_middle,
            self.daemon_middle_second,
            self.daemon_second,
            self.utterance_output,
            self.ailalubar_output,
            self.azazuley_output,
            self.ailalaza_output,
            self.leysyff_output,
            self.ffysyel_output,
            self.definition_output,
            self.canon_glossary_output,
            self.glossolalia_output,
            self.ailalossolg_output,
        )

    def set_text_colors(
        self,
        background: str,
        text: str,
        selection_background: str,
        selection_text: str,
    ) -> None:
        for widget in self._content_widgets():
            palette = widget.palette()
            palette.setColor(QPalette.ColorRole.Base, QColor(background))
            palette.setColor(QPalette.ColorRole.Text, QColor(text))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(selection_background))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(selection_text))
            widget.setPalette(palette)

        self._set_scripture_surface_colors(background, text)

        mirror_text = QColor(text).darker(165)
        for mirror in (
            self.daemon_first,
            self.daemon_second,
        ):
            palette = mirror.palette()
            palette.setColor(QPalette.ColorRole.Text, mirror_text)
            mirror.setPalette(palette)

    def set_tab_colors(self, background: str, text: str, body: str) -> None:
        self.output_tabs.tabBar().setStyleSheet(
            "QTabBar::tab {"
            f"background: {body};"
            f"color: {text};"
            "border: 1px solid " + text + ";"
            "padding: 5px 12px;"
            "}"
            "QTabBar::tab:selected {"
            f"background: {background};"
            f"color: {text};"
            "}"
        )

    def set_daemon_tongue(self, first: str, middle: str, second: str, middle_second: str | None = None) -> None:
        self.daemon_first.setText(first)
        self.daemon_middle.setText(middle)
        self.daemon_middle_second.setText(middle if middle_second is None else middle_second)
        self.daemon_second.setText(second)

    def set_mirror_utterance(self, grimchain: str) -> None:
        """Project the finite source into the authored four-field 12-glyph house."""
        left_reflection = grimchain[:12][::-1]
        right_reflection = grimchain[-12:][::-1]
        self.set_daemon_tongue(
            left_reflection,
            grimchain[:12],
            right_reflection,
            grimchain[-12:],
        )

    def set_utterance(self, value: str) -> None:
        self.utterance_output.setPlainText(value)
        format_exact_grimchain(self.utterance_output, value)

    def set_ailalubar(self, reflection: AilalubarReflection) -> None:
        """Paint exactly one reflected Prosody string under normal exact-font rules."""
        if not isinstance(reflection, AilalubarReflection):
            raise TypeError("Ailalubar requires its exact reflection authority")
        self.ailalubar_output.setPlainText(reflection.mirrored_source)
        format_exact_grimchain(self.ailalubar_output, reflection.mirrored_source)

    def ailalubar_render_witness(self, reflection: AilalubarReflection) -> AilalubarRenderWitness:
        """Mint the final witness from the exact layout model that actually paints Ailalubar."""
        if not isinstance(reflection, AilalubarReflection):
            raise TypeError("Ailalubar witness requires its exact reflection authority")
        if self.ailalubar_output.toPlainText() != reflection.mirrored_source:
            raise ValueError("Ailalubar surface is detached from its reflection authority")

        model = self.ailalubar_output.exactLayoutModel()
        mirrored = reflection.mirrored_source
        boundaries: dict[int, int] = {}
        qt = 0
        for index, character in enumerate(mirrored):
            boundaries[qt] = index
            qt += qt_utf16_units(character)

        level_by_qt: dict[int, int] = {}
        for run in model.runs:
            run_qt = run.qt_start
            for character in run.text:
                level_by_qt[run_qt] = run.bidi_level
                run_qt += qt_utf16_units(character)

        source_positions: list[int] = []
        levels: list[int] = []
        mirrored_flags: list[bool] = []
        for character, mirrored_qt in model.cantillation:
            try:
                mirrored_index = boundaries[mirrored_qt]
            except KeyError as exc:
                raise ValueError(
                    f"Cantillation position is not a Prosody code-point boundary: {mirrored_qt}"
                ) from exc
            source_positions.append(len(reflection.source) - 1 - mirrored_index)
            try:
                bidi_level = level_by_qt[mirrored_qt]
            except KeyError as exc:
                raise ValueError(
                    f"Cantillation position has no exact layout run: {mirrored_qt}"
                ) from exc
            levels.append(bidi_level)
            # Metadata only: this never selects, substitutes, flips, or reverses a glyph.
            mirrored_flags.append(
                bool(unicodedata.mirrored(character) and bidi_level & 1)
            )

        return AilalubarRenderWitness(
            source=reflection.source,
            mirrored_source=reflection.mirrored_source,
            visual_text=model.cantillation_text,
            visual_source_positions=tuple(source_positions),
            visual_levels=tuple(levels),
            visual_mirrored_flags=tuple(mirrored_flags),
            source_face_ids=reflection.source_face_ids,
            source_face_runs=reflection.source_face_runs,
            rendering_authority_sha256=reflection.rendering_authority_sha256,
            point_size=reflection.point_size,
            layout_direction=reflection.layout_direction,
        )

    def _apply_presentation_spans(
        self,
        widget: ExactFontTextEdit,
        spans: tuple[PresentationSpan, ...],
        allowed_roles: frozenset[str],
    ) -> None:
        document_units = len(widget.toPlainText().encode("utf-16-le")) // 2
        for span in spans:
            if span.semantic_role not in allowed_roles:
                raise ValueError(f"unsupported presentation role: {span.semantic_role!r}")
            if span.qt_end > document_units:
                raise ValueError(f"presentation span exceeds document: {span!r}")
            if widget.textForUtf16Range(span.qt_start, span.qt_end) != span.rendered_text:
                raise ValueError(f"presentation span text/provenance mismatch: {span!r}")
            if not isinstance(widget, ExactFontTextEdit):
                raise TypeError("authored lexical rendering requires ExactFontTextEdit")
            font_file = authored_lexical_font_file(span.font_family, span.source_authority)
            widget.add_exact_font_span(span.qt_start, span.rendered_text, span.font_family, font_file)

    def _set_written_projection(
        self,
        widget: ExactFontTextEdit,
        value: str,
        runs: tuple[PresentationSpan, ...],
    ) -> None:
        widget.setPlainText(value)
        breath_face = grimchain_face_for_character(BREATH_SEPARATOR)
        for index, span in enumerate(runs):
            font_file = authored_lexical_font_file(span.font_family, span.source_authority)
            widget.add_exact_font_span(span.qt_start, span.rendered_text, span.font_family, font_file)
            if index + 1 < len(runs):
                widget.add_exact_font_span(span.qt_end, BREATH_SEPARATOR, breath_face.family, breath_face.file)

    def set_azazuley(self, value: str, runs: tuple[PresentationSpan, ...] = ()) -> None:
        self._set_written_projection(self.azazuley_output, value, runs)

    def set_ailalaza(self, value: str, runs: tuple[PresentationSpan, ...] = ()) -> None:
        self._set_written_projection(self.ailalaza_output, value, runs)

    def set_glossolalia(self, value: str) -> None:
        self.glossolalia_output.setPlainText(value)
        _format_exact_prose_uncovered(self.glossolalia_output)

    def set_ailalossolg(self, value: str) -> None:
        self.ailalossolg_output.setPlainText(value)
        _format_exact_prose_uncovered(self.ailalossolg_output)

    def set_definition(self, value: str, runs: tuple[PresentationSpan, ...] = ()) -> None:
        self.definition_output.setPlainText(value)
        self._apply_presentation_spans(
            self.definition_output, runs, frozenset({"definition_word"})
        )
        format_definition_grimchains(self.definition_output, value)
        _format_exact_prose_uncovered(self.definition_output)

    def set_definition_presentation(self, presentation: DefinitionPresentation) -> None:
        self.definition_output.setPlainText(presentation.text)
        self._apply_presentation_spans(
            self.definition_output, presentation.lexical_spans, frozenset({"definition_word"})
        )
        for entry in presentation.entries:
            for field in entry.fields:
                if field.semantic_role == "grimchain" and field.value:
                    format_exact_grimchain_span(
                        self.definition_output, field.qt_value_start, field.value
                    )
        _format_exact_prose_uncovered(self.definition_output)

    def set_leysyff_presentation(self, presentation: LeySyffPresentation) -> None:
        self.leysyff_output.setPlainText(presentation.text)
        self.leysyff_output.setForcedLeftToRightLayout(True)
        self.leysyff_output.setAlignment(Qt.AlignmentFlag.AlignLeft)
        _format_ostensive_paragraph_markers(self.leysyff_output)
        _format_exact_prose_uncovered(self.leysyff_output)
        self._refresh_scripture_geometry()

    def set_ffysyel(self, presentation: LeySyffPresentation) -> None:
        self.ffysyel_output.setPlainText(presentation.text)
        self.ffysyel_output.setForcedLeftToRightLayout(False)
        self.ffysyel_output.setAlignment(Qt.AlignmentFlag.AlignRight)
        _format_ostensive_paragraph_markers(self.ffysyel_output)
        _format_exact_prose_uncovered(self.ffysyel_output)
        self._refresh_scripture_geometry()

    def show_error(self, value: str) -> None:
        self.definition_output.setPlainText(value)
        _format_exact_prose_uncovered(self.definition_output)
