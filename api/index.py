import os
import shutil
import sys
from pathlib import Path

# Add src and root to path so canopytrace can be imported on Vercel
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
DATA_DIR = ROOT_DIR / "data"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure offline database is available in writable /tmp location on serverless
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    tmp_data = Path("/tmp/canopytrace/data")
    tmp_data.mkdir(parents=True, exist_ok=True)
    tmp_db = tmp_data / "reference.db"
    bundled_db = DATA_DIR / "reference.db"
    if not tmp_db.exists():
        if bundled_db.exists():
            try:
                shutil.copy2(bundled_db, tmp_db)
            except Exception:
                pass
        if not tmp_db.exists():
            try:
                from canopytrace.db.seed import seed_database
                seed_database(tmp_db, DATA_DIR)
            except Exception as e:
                print(f"[CanopyTrace Vercel Init] Database seed warning: {e}")
    os.environ["CANOPYTRACE_DB_PATH"] = str(tmp_db)

os.environ.setdefault("CANOPYTRACE_MOCK_HARNESS", "1")

from canopytrace.web.app import app

# Vercel looks for 'app' or 'handler'
handler = app
