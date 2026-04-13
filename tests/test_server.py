import json
import threading
import unittest
import urllib.request

from gradient_adk.server import create_server, invoke_entrypoint


def test_entrypoint(payload, context):
    return {"prompt": payload.get("prompt"), "trace": context.get("trace")}


class ServerTests(unittest.TestCase):
    def test_invoke_entrypoint_passes_payload_and_context(self):
        result = invoke_entrypoint(test_entrypoint, {"prompt": "hi"}, {"trace": "abc"})
        self.assertEqual(result, {"prompt": "hi", "trace": "abc"})

    def test_health_endpoint_returns_ok(self):
        server = create_server(test_entrypoint, host="127.0.0.1", port=0)
        port = server.server_address[1]
        thread = threading.Thread(target=server.handle_request)
        thread.start()
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health") as resp:
                body = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(resp.status, 200)
                self.assertEqual(body, {"status": "ok"})
        finally:
            thread.join(timeout=2)
            server.server_close()


if __name__ == "__main__":
    unittest.main()
