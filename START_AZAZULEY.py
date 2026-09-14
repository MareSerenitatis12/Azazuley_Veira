#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import importlib.util
import os
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

# Always run the live source tree. Never write Python bytecode state.
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

if importlib.util.find_spec("PySide6") is None:
    raise SystemExit(
        "Azazuley requires PySide6 for the development UI.\n"
        "Install the project dependency into the Python environment you are using:\n\n"
        f"    {sys.executable} -m pip install -r {ROOT / 'requirements-dev.txt'}\n"
    )

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from azazuley_veira.app import run

raise SystemExit(run())
