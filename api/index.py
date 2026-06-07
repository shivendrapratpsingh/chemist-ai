import sys
import os

# Add both repo root AND backend/ to path so `import database` works inside main.py
_root    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_backend = os.path.join(_root, "backend")
sys.path.insert(0, _backend)
sys.path.insert(0, _root)

from backend.main import app  # noqa: F401 — Vercel picks up `app`
