"""Local development server for running ADK agents."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable


def invoke_entrypoint(
    entrypoint_func: Callable[[dict[str, Any], dict[str, Any]], Any],
    payload: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> Any:
    return entrypoint_func(payload, context or {})


def create_server(
    entrypoint_func: Callable[[dict[str, Any], dict[str, Any]], Any],
    host: str = "0.0.0.0",
    port: int = 8080,
) -> ThreadingHTTPServer:
    class RunHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                body = json.dumps({"status": "ok"}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/run":
                self.send_response(404)
                self.end_headers()
                return

            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length)
                data = json.loads(raw.decode("utf-8") or "{}")
                if not isinstance(data, dict):
                    raise ValueError("Request body must be a JSON object")

                payload = data.get("payload", data)
                context = data.get("context", {})
                result = invoke_entrypoint(entrypoint_func, payload, context)
                body = json.dumps({"result": result}).encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as exc:  # pragma: no cover
                body = json.dumps({"error": str(exc)}).encode("utf-8")
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

    return ThreadingHTTPServer((host, port), RunHandler)


def run_server(
    entrypoint_func: Callable[[dict[str, Any], dict[str, Any]], Any],
    host: str = "0.0.0.0",
    port: int = 8080,
) -> None:
    server = create_server(entrypoint_func, host=host, port=port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
