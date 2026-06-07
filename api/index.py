import sys
import os

# Add project root to path so backend modules are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app  # noqa: F401 — Vercel picks up `app`
