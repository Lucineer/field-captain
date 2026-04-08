"""Field Captain - Jetson field agent with voice interface and git-agent orchestration."""
import json, os, subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

DATA_DIR = Path(os.getenv("FIELD_CAPTAIN_DATA", ".field_captain"))
DATA_DIR.mkdir(exist_ok=True)
STATUS_FILE = DATA_DIR / "status.json"

def get_status():
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text())
    return {"mode": "idle", "vessels": [], "uptime": 0}

def save_status(data):
    STATUS_FILE.write_text(json.dumps(data, indent=2))

def list_vessels():
    """List known vessel repos in the workspace."""
    workspace = Path(os.getenv("FIELD_CAPTAIN_WORKSPACE", os.getcwd()))
    vessels = []
    for d in workspace.iterdir():
        if d.is_dir() and (d / "vessel.json").exists():
            try:
                cfg = json.loads((d / "vessel.json").read_text())
                vessels.append({"name": d.name, "description": cfg.get("description", ""), "status": "ready"})
            except Exception:
                vessels.append({"name": d.name, "status": "unknown"})
    return vessels

def run_git(args):
    try:
        result = subprocess.run(["git"] + args, capture_output=True, text=True, timeout=30)
        return {"stdout": result.stdout.strip(), "stderr": result.stderr.strip(), "code": result.returncode}
    except Exception as e:
        return {"error": str(e), "code": -1}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self._json({"status": "ok", "mode": get_status()["mode"]})
        elif self.path == "/status":
            status = get_status()
            status["vessels"] = list_vessels()
            self._json(status)
        elif self.path == "/vessels":
            self._json(list_vessels())
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        if self.path == "/command":
            result = run_git([body.get("command", "")] + body.get("args", []))
            self._json(result)
        elif self.path == "/status":
            save_status(body)
            self._json({"saved": True})
        else:
            self._json({"error": "not found"}, 404)

    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8420"))
    print(f"Field Captain listening on :{port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
