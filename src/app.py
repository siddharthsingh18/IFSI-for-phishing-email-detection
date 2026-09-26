"""Streamlit entry point for src/app.py, delegating to the main application."""

import runpy
from pathlib import Path

root_app = Path(__file__).resolve().parents[1] / "app.py"
runpy.run_path(str(root_app), run_name="__main__")
