from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from azazuley_veira.config.font_runtime import load_installed_fonts
from azazuley_veira.ui.main_window import MainWindow


def run() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Azazuley Veira")
    load_installed_fonts()
    window = MainWindow()
    window.show()
    return app.exec()
