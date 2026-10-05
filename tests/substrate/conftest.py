"""Import eunoia from EUNOIA_SRC when set (the SUB-1 mutation harness points it at a mutated copy), else from
this checkout's src/. Inserted first so an installed copy cannot shadow the code under test."""
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, os.environ.get("EUNOIA_SRC") or str(ROOT / "src"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
