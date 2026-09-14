"""Read-only Azazuley help document viewer."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser

HELP_FILE = Path(__file__).resolve().parents[3] / "docs" / "HELP.md"


class HelpViewer(QDialog):
    """Render the packaged Markdown help as a read-only document."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Azazuley Veira Help")
        self.resize(820, 680)

        if not HELP_FILE.is_file():
            raise RuntimeError(f"Azazuley help document is missing: {HELP_FILE}")

        document = QTextBrowser(self)
        document.setOpenExternalLinks(True)
        document.setMarkdown(HELP_FILE.read_text(encoding="utf-8"))

        layout = QVBoxLayout(self)
        layout.addWidget(document)
