from __future__ import annotations

import sys
from pathlib import Path

# Ensure the repository root is importable in the serverless runtime.
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend import app
