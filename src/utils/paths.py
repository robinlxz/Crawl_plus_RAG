import sys
from pathlib import Path

# Resolve the project root directory
# src/utils/paths.py -> ../../ -> rag_project root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = ROOT_DIR / "data"
CONFIG_DIR = ROOT_DIR / "config"
SRC_DIR = ROOT_DIR / "src"

# Helper to ensure src is in python path
def add_src_to_path():
    if str(SRC_DIR) not in sys.path:
        sys.path.append(str(SRC_DIR))
