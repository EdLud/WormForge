#!/usr/bin/env python3
"""Build or check this website's pinned catalogue sources."""
from pathlib import Path
import runpy

source = Path(__file__).resolve().parent.parent / "catalogue/tools/publish-packs.py"
if not source.is_file():
    raise SystemExit("Initialize catalogue first: git submodule update --init --recursive")
runpy.run_path(str(source), run_name="__main__")
