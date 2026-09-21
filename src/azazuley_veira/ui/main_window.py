from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QAbstractListModel, QModelIndex, QRegularExpression, Qt
from PySide6.QtGui import QAction, QColor, QFont, QFontDatabase, QPalette, QRegularExpressionValidator, QResizeEvent, QTextCharFormat
from PySide6.QtWidgets import (
    QBoxLayout,
    QColorDialog,
    QComboBox,
    QGraphicsDropShadowEffect,
    QLabel,
    QFileDialog,
    QLineEdit,
    QMainWindow,
    QMenu,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from azazuley_veira.ailalubar_render import render_ailalubar
from azazuley_veira.config import font_catalog, visual
from azazuley_veira.config.font_runtime import DEFAULT_POINT_SIZE
from azazuley_veira.engines import emanation, grimchain, sydonic
from azazuley_veira import grimchain_journal
from azazuley_veira.grimchain_journal import GrimchainHistorySession, append_grimchain, read_grim_import
from azazuley_veira.ui.help_viewer import HelpViewer
from azazuley_veira.ui.terminal import SubmitTextEdit, Terminal
from azazuley_veira.ui.exact_text import format_exact_grimchain, write_exact_surface_groups_pdf


class _GrimchainHistoryModel(QAbstractListModel):
    PAGE_SIZE = 40

    def __init__(self, parent=None):
        super().__init__(parent)
        self._session: GrimchainHistorySession | None = None
        self._records: list[tuple[str, str, str]] = []

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else 1 + len(self._records)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        if row == 0:
            if role == Qt.ItemDataRole.DisplayRole:
                return "GrimChain History"
            return None
        if not 1 <= row <= len(self._records):
            return None
        timestamp, user_input, chain = self._records[row - 1]
        if role == Qt.ItemDataRole.DisplayRole:
            return f"{timestamp} | {user_input}"
        if role == Qt.ItemDataRole.UserRole:
            return chain
        return None

    def start_session(self) -> None:
        self.close_session()
        self.beginResetModel()
        self._records = []
        self._session = GrimchainHistorySession()
        self.endResetModel()
        self.fetchMore()

    def close_session(self) -> None:
        if self._session is not None:
            self._session.close()
            self._session = None
        if self._records:
            self.beginResetModel()
            self._records = []
            self.endResetModel()

    def canFetchMore(self, parent=QModelIndex()) -> bool:
        return not parent.isValid() and self._session is not None and self._session.has_more

    def fetchMore(self, parent=QModelIndex()) -> None:
        if parent.isValid() or self._session is None or not self._session.has_more:
            return
        records = self._session.fetch(self.PAGE_SIZE)
        if not records:
            return
        first = 1 + len(self._records)
        last = first + len(records) - 1
        self.beginInsertRows(QModelIndex(), first, last)
        self._records.extend(records)
        self.endInsertRows()


class _GrimchainHistoryComboBox(QComboBox):
    def showPopup(self) -> None:
        model = self.model()
        if isinstance(model, _GrimchainHistoryModel):
            model.start_session()
        self.setCurrentIndex(0)
        super().showPopup()


class MainWindow(QMainWindow):
    """Responsive visible body of the Azazuley Veira terminal."""

    NARROW_WIDTH = 720
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Azazuley Veira")
        self.setMinimumSize(360, 300)
        self.resize(1180, 760)

        self.body = QWidget()
        self.body.setObjectName("body")
        self.setCentralWidget(self.body)

        self.layout = QVBoxLayout(self.body)
        self.layout.setSpacing(10)

        self._terminal_bg = visual.TERMINAL_BG
        self._font_color = visual.TEAL
        self._body_bg = visual.TSHIRT_GRAY

        self.header = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.header.setSpacing(10)

        self.grimchain_group = QVBoxLayout()
        self.grimchain_group.setSpacing(2)
        self.grimchain_label = QLabel("GrimChain>")
        self.grimchain_label.setObjectName("grimchainHeaderLabel")
        self.grimchain_group.addWidget(self.grimchain_label)
        self.grimchain_input = SubmitTextEdit(preferred_rows=2)
        self.grimchain_input.setObjectName("grimchainInput")
        self.grimchain_input.setLineWrapMode(SubmitTextEdit.LineWrapMode.WidgetWidth)
        self.grimchain_input.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.grimchain_input.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        header_control_height = 28
        self.grimchain_input.setFixedHeight(header_control_height)
        self.grimchain_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.grimchain_input.submitted.connect(self._submit_grimchain_bar)
        self.grimchain_group.addWidget(self.grimchain_input)
        self.header.addLayout(self.grimchain_group, 1)

        self.domus_group = QVBoxLayout()
        self.domus_group.setSpacing(2)
        self.domus_label = QLabel("Domus Count>")
        self.domus_label.setObjectName("domusHeaderLabel")
        self.domus_group.addWidget(self.domus_label)

        self.domus_count = QLineEdit()
        self.domus_count.setObjectName("domusCount")
        self.domus_count.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"^-?[0-9]*$"), self.domus_count)
        )
        self.domus_count.setPlaceholderText(
            "Please input your choice for the visible Domus Middle"
        )
        self.domus_count.setFixedWidth(78)
        self.domus_count.setFixedHeight(header_control_height)
        self.domus_count.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.domus_group.addWidget(self.domus_count)
        self.header.addLayout(self.domus_group)

        self.font_box = QComboBox()
        self.font_box.setObjectName("fontBox")
        self._populate_font_box()
        self.font_box.currentTextChanged.connect(self._set_terminal_font)

        self.color_group = QVBoxLayout()
        self.color_group.setSpacing(2)
        self.color_label = QLabel("COLORS:")
        self.color_label.setObjectName("colorHeaderLabel")
        self.color_group.addWidget(self.color_label)

        self.color_button = QPushButton("Choose...")
        self.color_button.setObjectName("colorButton")
        self.color_button.setMinimumWidth(92)
        self.color_button.setMaximumWidth(112)
        color_menu = QMenu(self.color_button)
        terminal_action = QAction("Terminal Background...", color_menu)
        font_action = QAction("Font Color...", color_menu)
        body_action = QAction("Body Background...", color_menu)
        terminal_action.triggered.connect(lambda: self._choose_color("terminal"))
        font_action.triggered.connect(lambda: self._choose_color("font"))
        body_action.triggered.connect(lambda: self._choose_color("body"))
        color_menu.addAction(terminal_action)
        color_menu.addAction(font_action)
        color_menu.addAction(body_action)
        self.color_button.setMenu(color_menu)
        self.color_group.addWidget(self.color_button)
        self.header.addLayout(self.color_group)

        self.import_button = QPushButton("IMPORT")
        self.import_button.setObjectName("importButton")
        self.import_button.setMinimumWidth(72)
        self.import_button.setMaximumWidth(88)

        self.export_button = QPushButton("EXPORT")
        self.export_button.setObjectName("exportButton")
        self.export_button.setMinimumWidth(72)
        self.export_button.setMaximumWidth(88)

        self.help_button = QPushButton("HELP")
        self.help_button.setObjectName("helpButton")
        self.help_button.setMinimumWidth(72)
        self.help_button.setMaximumWidth(88)
        self.help_button.clicked.connect(self._show_help)
        self.import_button.clicked.connect(self._import_grim_files)
        self.export_menu = QMenu(self.export_button)
        self._export_bio_action = self.export_menu.addAction("Export GrimChained Bio (.shk)")
        self._export_words_action = self.export_menu.addAction("Export Words & Definitions (PDF)")
        self._export_glossary_action = self.export_menu.addAction("Export Canon Glossary (PDF)")
        self._export_bio_action.triggered.connect(
            lambda _checked=False: self._run_export(self._export_grimchained_bio)
        )
        self._export_words_action.triggered.connect(
            lambda _checked=False: self._run_export(self._export_words_definitions_pdf)
        )
        self._export_glossary_action.triggered.connect(
            lambda _checked=False: self._run_export(self._export_canon_glossary_pdf)
        )
        self.export_menu.aboutToShow.connect(self._refresh_export_menu)
        self.export_button.setMenu(self.export_menu)

        self.top_row = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.top_row.setContentsMargins(0, 0, 0, 0)
        self.top_row.setSpacing(8)
        self.grimchain_history = _GrimchainHistoryComboBox()
        self.grimchain_history.setObjectName("grimchainHistory")
        self.grimchain_history.setMinimumWidth(280)
        self.grimchain_history.setMaxVisibleItems(30)
        self._grimchain_history_model = _GrimchainHistoryModel(self.grimchain_history)
        self.grimchain_history.setModel(self._grimchain_history_model)
        self.grimchain_history.activated.connect(self._load_history_grimchain)
        self.top_row.addWidget(self.grimchain_history)
        self.top_row.addStretch(1)
        self.top_row.addWidget(self.import_button)
        self.top_row.addWidget(self.export_button)
        self.top_row.addWidget(
            self.help_button,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        self.layout.addLayout(self.top_row)
        self.layout.addLayout(self.header)

        self.terminal = Terminal()
        self.grimchain_input.textChanged.connect(lambda: format_exact_grimchain(self.grimchain_input))
        self.terminal.setObjectName("terminal")
        self.terminal.set_user_font_selector(self.font_box)
        self.terminal.user_song_submitted.connect(self._submit_user_song)
        self.domus_count.returnPressed.connect(self._submit_domus_count)

        glow = QGraphicsDropShadowEffect(self.terminal)
        glow.setBlurRadius(24)
        glow.setOffset(0, 0)
        glow.setColor(visual.TEAL_FAINT)
        self.terminal.setGraphicsEffect(glow)
        self.layout.addWidget(self.terminal, 1)

        self._apply_style()
        self._choose_initial_font()
        self._apply_responsive_geometry(self.width())

    def _load_history_grimchain(self, index: int) -> None:
        self.statusBar().clearMessage()
        chain = self.grimchain_history.itemData(index, Qt.ItemDataRole.UserRole)
        if isinstance(chain, str) and chain:
            self.grimchain_input.setPlainText(chain)
        self._grimchain_history_model.close_session()
        self.grimchain_history.setCurrentIndex(0)

    def _import_grim_files(self) -> None:
        paths, _selected_filter = QFileDialog.getOpenFileNames(
            self, "Import Grim files", "", "Grim files (*.grim)"
        )
        if not paths:
            return
        records: list[tuple[str, str]] = []
        try:
            for path in paths:
                imported = read_grim_import(path)
                for _user_input, chain in imported:
                    grimchain.validate(chain)
                records.extend(imported)
        except (OSError, UnicodeError, ValueError) as exc:
            self.terminal.show_error(str(exc))
            return
        for user_input, chain in records:
            append_grimchain(user_input, chain)

    def _export_directory(self) -> Path:
        destination = Path.home() / ".grimchain" / "azazuley" / "exports"
        destination.mkdir(parents=True, exist_ok=True)
        return destination

    def _export_depth_text(self) -> str:
        middle_text = self.domus_count.text().strip()
        depth = int(middle_text) if middle_text else 0
        if depth < 0:
            depth = 0
        return str(depth)

    def _words_definition_groups(self) -> tuple[tuple[object, ...], ...]:
        return (
            (self.terminal.utterance_output,),
            (self.terminal.ailalubar_output,),
            (self.terminal.azazuley_output,),
            (self.terminal.ailalaza_output,),
            (self.terminal.glossolalia_output,),
            (self.terminal.ailalossolg_output,),
            (self.terminal.leysyff_output, self.terminal.ffysyel_output),
            (self.terminal.definition_output,),
        )

    @staticmethod
    def _export_section_header(name: str) -> str:
        rule = "⧟" * 27
        return f"{rule}\n{name}\n{rule}\n\n"

    def _words_definition_section_headers(self) -> tuple[str, ...]:
        return tuple(
            self._export_section_header(name)
            for name in (
                "Rabulalia",
                "Ailalubar",
                "Azalalia",
                "Ailalaza",
                "Glossolalia",
                "Ailalossolg",
                "LeySyff/FfysYel",
                "Definition",
            )
        )

    def _refresh_export_menu(self) -> None:
        active = grimchain_journal.ACTIVE_JOURNAL
        self._export_bio_action.setEnabled(active.is_file() and active.stat().st_size > 0)
        self._export_words_action.setEnabled(
            all(any(bool(surface.toPlainText()) for surface in group) for group in self._words_definition_groups())
        )
        self._export_glossary_action.setEnabled(bool(self.terminal.canon_glossary_output.toPlainText()))

    def _run_export(self, operation) -> None:
        try:
            destination = operation()
        except (OSError, RuntimeError, UnicodeError, ValueError) as exc:
            self.terminal.show_error(str(exc))
            return
        self.statusBar().showMessage(f"Exported {destination}")

    def _export_grimchained_bio(self) -> Path:
        source = grimchain_journal.ensure_grimchain_journal()
        if source.stat().st_size == 0:
            raise ValueError("there is no active GrimChain .bio to export")
        depth = self._export_depth_text()
        code, chain = grimchain.file(source, depth)
        if code != 0:
            raise RuntimeError(chain)
        destination = self._export_directory() / "grimchains.shk"
        destination.parent.mkdir(parents=True, exist_ok=True)
        original = source.read_bytes()
        prefix = original if original.endswith(b"\n") else original + b"\n"
        temporary = destination.with_name(destination.name + ".tmp")
        try:
            temporary.write_bytes(prefix + chain.encode("utf-8") + b"\n")
            temporary.replace(destination)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
        return destination

    def _embed_export_pdf(self, destination: Path) -> Path:
        code, result = grimchain.pdf_embed(destination, self._export_depth_text())
        if code != 0:
            destination.unlink(missing_ok=True)
            raise RuntimeError(result)
        return destination

    def _export_words_definitions_pdf(self) -> Path:
        groups = self._words_definition_groups()
        if not all(any(bool(surface.toPlainText()) for surface in group) for group in groups):
            raise ValueError("render a GrimChain before exporting Words & Definitions")
        destination = self._export_directory() / "Azazuley Words and Definitions.pdf"
        destination.parent.mkdir(parents=True, exist_ok=True)
        write_exact_surface_groups_pdf(
            groups,
            destination,
            section_headers=self._words_definition_section_headers(),
        )
        return self._embed_export_pdf(destination)

    def _export_canon_glossary_pdf(self) -> Path:
        destination = self._export_directory() / "Canon Glossary.pdf"
        destination.parent.mkdir(parents=True, exist_ok=True)
        write_exact_surface_groups_pdf(
            ((self.terminal.canon_glossary_output,),),
            destination,
            section_headers=(self._export_section_header("Canon Glossary"),),
        )
        return self._embed_export_pdf(destination)

    def _show_help(self) -> None:
        viewer = HelpViewer(self)
        viewer.exec()

    def _choose_color(self, target: str) -> None:
        current = {
            "terminal": self._terminal_bg,
            "font": self._font_color,
            "body": self._body_bg,
        }[target]
        title = {
            "terminal": "Terminal Background Color",
            "font": "Font Color",
            "body": "Body Background Color",
        }[target]
        chosen = QColorDialog.getColor(
            QColor(current),
            self,
            title,
            QColorDialog.ColorDialogOption.DontUseNativeDialog,
        )
        if not chosen.isValid():
            return
        value = chosen.name(QColor.NameFormat.HexRgb)
        if target == "terminal":
            self._terminal_bg = value
        elif target == "font":
            self._font_color = value
        else:
            self._body_bg = value
        self._apply_style()

    def _populate_font_box(self) -> None:
        self.font_box.addItem(font_catalog.SYSTEM_DEFAULT)
        for family in sorted(QFontDatabase.families(), key=str.casefold):
            self.font_box.addItem(family)

    def _choose_initial_font(self) -> None:
        index = self.font_box.findText(font_catalog.SYSTEM_DEFAULT)
        if index < 0:
            raise RuntimeError("system default input font entry is missing")
        self.font_box.setCurrentIndex(index)
        self._set_terminal_font(font_catalog.SYSTEM_DEFAULT)

    def _set_terminal_font(self, family: str) -> None:
        if family == font_catalog.SYSTEM_DEFAULT:
            resolved_family = font_catalog.DEFAULT_FAMILY
            selected = QFont(resolved_family, DEFAULT_POINT_SIZE)
        else:
            if family not in QFontDatabase.families():
                raise RuntimeError(f"user-selected font is not available: {family}")
            selected = QFont(family, DEFAULT_POINT_SIZE)
            resolved_family = family

        user_song = self.terminal.user_song
        cursor = user_song.textCursor()
        if cursor.hasSelection():
            character_format = QTextCharFormat()
            character_format.setFont(selected)
            cursor.mergeCharFormat(character_format)
            user_song.setTextCursor(cursor)
            return
        user_song.setFont(selected)
        user_song.document().setDefaultFont(selected)

    def _submit_grimchain_bar(self, chain: str | None = None) -> None:
        if chain is None:
            chain = self.grimchain_input.toPlainText()
        if not chain:
            return

        self.statusBar().clearMessage()
        try:
            grimchain.validate(chain)
        except ValueError:
            message = "The GrimChain was malformed, check you GrimSpelling and Grim again"
            self.terminal.show_error(message)
            return

        self._render_selected(chain, chain, cadence_translation=False)

    def _submit_domus_count(self) -> None:
        source = self.terminal.user_song.toPlainText()
        if source == "":
            return
        self._submit_user_song(source)

    def _submit_user_song(self, source: str) -> None:
        if source == "":
            return

        self.statusBar().clearMessage()
        try:
            middle_text = self.domus_count.text().strip()
            if not middle_text:
                code, chain = grimchain.string_cli(source, "")
                if code != 0:
                    self.terminal.show_error(chain)
                    return
                self.grimchain_input.setPlainText(chain)
                self._render_selected(chain, source, cadence_translation=True)
                return
            requested_depth = int(middle_text)
            if requested_depth < 0:
                requested_depth = 0
            session = grimchain.GrimChainContinuationSession(source, requested_depth)
        except Exception as exc:
            self.terminal.show_error(f"grimchain: {exc}")
            return

        try:
            unfold = sydonic._SYDONIC_ENGINE.resolve_grimchain_unfold(
                requested_depth, session.chain_at
            )
            chain = unfold.final_chain
        except grimchain.GrimChainContinuationError as exc:
            self.terminal.show_error(f"grimchain: {exc}")
            return
        except Exception as exc:
            self.terminal.show_error(f"{exc.__class__.__name__}: {exc}")
            return

        try:
            grimchain.validate(chain)
        except ValueError as exc:
            self.terminal.show_error(str(exc))
            return

        self.grimchain_input.setPlainText(chain)
        self._render_selected(chain, source, cadence_translation=False)
        if unfold.additional_depth > 0:
            self.statusBar().showMessage(
                f"Sydonic unfolded +{unfold.additional_depth}: requested {unfold.requested_depth} → "
                f"final {unfold.final_depth}. Full same GrimChain saved to .bio."
            )

    def _render_selected(self, chain: str, user_input: str, *, cadence_translation: bool) -> None:
        append_grimchain(user_input, chain)
        chain = emanation.grimchain_emanate(chain)
        self.terminal.set_mirror_utterance(chain)
        self.terminal.set_utterance(chain)

        reflection = render_ailalubar(chain, self.terminal.ailalubar_output.pointSizeF())
        self.terminal.set_ailalubar(reflection)
        mirror_witness = self.terminal.ailalubar_render_witness(reflection)

        try:
            transaction = sydonic.render_transaction(mirror_witness, cadence_translation=cadence_translation)
        except Exception as exc:
            self.terminal.show_error(f"{exc.__class__.__name__}: {exc}")
            return

        self._render_transaction = transaction
        self.terminal.set_azazuley(
            transaction.azalalia_body,
            transaction.azalalia_runs,
        )
        self.terminal.set_ailalaza(
            transaction.ailalaza_body,
            transaction.ailalaza_runs,
        )
        self.terminal.set_glossolalia(transaction.glossolalia_body)
        self.terminal.set_ailalossolg(transaction.ailalossolg_body)
        self.terminal.set_leysyff_presentation(transaction.leysyff)
        self.terminal.set_ffysyel(transaction.ffysyel)
        self.terminal.set_definition_presentation(transaction.definition)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._apply_responsive_geometry(event.size().width())

    def _apply_responsive_geometry(self, width: int) -> None:
        narrow = width < self.NARROW_WIDTH
        if narrow:
            self.header.setDirection(QBoxLayout.Direction.TopToBottom)
            self.font_box.setMinimumWidth(140)
            self.font_box.setMaximumWidth(190)
            self.layout.setContentsMargins(10, 10, 10, 10)
            self.layout.setSpacing(8)
        else:
            self.header.setDirection(QBoxLayout.Direction.LeftToRight)
            self.font_box.setMinimumWidth(140)
            self.font_box.setMaximumWidth(190)
            margin = 20 if width < 1500 else 28
            self.layout.setContentsMargins(margin, 18, margin, margin)
            self.layout.setSpacing(10)

    def _apply_style(self) -> None:
        body_palette = self.body.palette()
        body_palette.setColor(QPalette.ColorRole.Window, QColor(self._body_bg))
        body_palette.setColor(QPalette.ColorRole.WindowText, QColor(self._font_color))
        self.body.setAutoFillBackground(True)
        self.body.setPalette(body_palette)

        terminal_palette = self.terminal.palette()
        terminal_palette.setColor(QPalette.ColorRole.Window, QColor(self._terminal_bg))
        terminal_palette.setColor(QPalette.ColorRole.WindowText, QColor(self._font_color))
        self.terminal.setAutoFillBackground(True)
        self.terminal.setPalette(terminal_palette)

        for label in (self.grimchain_label, self.domus_label, self.color_label):
            palette = label.palette()
            palette.setColor(QPalette.ColorRole.WindowText, QColor(self._font_color))
            label.setPalette(palette)
            label.setStyleSheet("font-size: 8pt;")

        grimchain_palette = self.grimchain_input.palette()
        grimchain_palette.setColor(QPalette.ColorRole.Base, QColor(self._terminal_bg))
        grimchain_palette.setColor(QPalette.ColorRole.Text, QColor(self._font_color))
        grimchain_palette.setColor(QPalette.ColorRole.Highlight, QColor(visual.TEAL_DIM))
        grimchain_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(visual.TERMINAL_BG_DEEP))
        self.grimchain_input.setPalette(grimchain_palette)

        domus_palette = self.domus_count.palette()
        domus_palette.setColor(QPalette.ColorRole.Base, QColor(self._terminal_bg))
        domus_palette.setColor(QPalette.ColorRole.Text, QColor(self._font_color))
        domus_palette.setColor(QPalette.ColorRole.Highlight, QColor(visual.TEAL_DIM))
        domus_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(visual.TERMINAL_BG_DEEP))
        self.domus_count.setPalette(domus_palette)

        control_palette = self.font_box.palette()
        control_palette.setColor(QPalette.ColorRole.Button, QColor(visual.TSHIRT_DARK))
        control_palette.setColor(QPalette.ColorRole.Base, QColor(visual.TSHIRT_DARK))
        control_palette.setColor(QPalette.ColorRole.ButtonText, QColor(visual.TEAL_SOFT))
        control_palette.setColor(QPalette.ColorRole.Text, QColor(visual.TEAL_SOFT))
        control_palette.setColor(QPalette.ColorRole.Highlight, QColor(visual.TEAL_DIM))
        control_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(visual.TERMINAL_BG_DEEP))
        self.font_box.setPalette(control_palette)
        self.color_button.setPalette(control_palette)
        self.import_button.setPalette(control_palette)
        self.export_button.setPalette(control_palette)
        self.help_button.setPalette(control_palette)

        self.terminal.set_text_colors(
            self._terminal_bg,
            self._font_color,
            visual.TEAL_DIM,
            visual.TERMINAL_BG_DEEP,
        )
        self.terminal.set_tab_colors(
            self._terminal_bg,
            self._font_color,
            self._body_bg,
        )
