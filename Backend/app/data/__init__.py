from pathlib import Path

ROOT = Path(__file__).resolve().parent
(ROOT / "uploads").mkdir(exist_ok=True)
