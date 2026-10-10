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

from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.requests import Request
from starlette.responses import JSONResponse
from canopytrace.web.app import app


class VercelPathMiddleware:
    def __init__(self, asgi_app: ASGIApp):
        self.asgi_app = asgi_app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] in ("http", "websocket"):
            headers = dict(scope.get("headers", []))
            orig_path = (
                headers.get(b"x-matched-path")
                or headers.get(b"x-forwarded-uri")
                or headers.get(b"x-original-uri")
            )
            if orig_path:
                try:
                    path_str = orig_path.decode("utf-8").split("?")[0]
                    if path_str and path_str != "/api/index.py":
                        scope["path"] = path_str
                        scope["raw_path"] = path_str.encode("utf-8")
                except Exception:
                    pass
        await self.asgi_app(scope, receive, send)


@app.get("/api/index.py")
async def vercel_diagnostic(request: Request):
    """Fallback diagnostic endpoint when requests hit /api/index.py directly."""
    return JSONResponse({
        "status": "healthy",
        "service": "CanopyTrace Forensic API",
        "message": "Direct endpoint hit on api/index.py",
        "matched_path": request.headers.get("x-matched-path"),
        "headers": {k: v for k, v in request.headers.items() if not k.startswith("sec-") and "auth" not in k.lower()}
    })


# Wrap with VercelPathMiddleware
handler = VercelPathMiddleware(app)
