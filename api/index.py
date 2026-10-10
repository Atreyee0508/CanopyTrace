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

from urllib.parse import parse_qs, urlencode, unquote
from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.requests import Request
from starlette.responses import JSONResponse
from canopytrace.web.app import app


class VercelPathMiddleware:
    def __init__(self, asgi_app: ASGIApp):
        self.asgi_app = asgi_app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] in ("http", "websocket"):
            qs_bytes = scope.get("query_string", b"")
            qs_str = qs_bytes.decode("utf-8")
            parsed_qs = parse_qs(qs_str, keep_blank_values=True)
            
            if "path" in parsed_qs:
                target_path = parsed_qs.pop("path")[0]
                if not target_path.startswith("/"):
                    target_path = "/" + target_path
                scope["path"] = target_path
                scope["raw_path"] = target_path.encode("utf-8")
                # Rebuild remaining query string without 'path'
                flat_qs = [(k, v) for k, values in parsed_qs.items() for v in values]
                scope["query_string"] = urlencode(flat_qs).encode("utf-8")
            elif scope.get("path") in ("/api/index.py", "/api/index"):
                # Default root route when invoked directly
                scope["path"] = "/"
                scope["raw_path"] = b"/"

        await self.asgi_app(scope, receive, send)


# Wrap with VercelPathMiddleware
handler = VercelPathMiddleware(app)
