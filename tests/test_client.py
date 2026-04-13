import json
import unittest
import urllib.error
from io import BytesIO
from unittest.mock import MagicMock, patch

from gradient_adk.client import GradientAPIError, GradientClient


def _make_response(data: object, status: int = 200):
    body = json.dumps(data).encode("utf-8")
    mock = MagicMock()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    mock.read.return_value = body
    mock.status = status
    return mock


class ClientTests(unittest.TestCase):
    def _client(self):
        return GradientClient(api_key="test-key", api_base="https://example.com/v1")

    def test_deploy_agent_calls_correct_endpoint(self):
        resp = _make_response({"agent_id": "ag-1", "status": "deploying"})
        with patch("urllib.request.urlopen", return_value=resp) as mock_open:
            result = self._client().deploy_agent("myagent", "agent:entry", "nyc3")

        self.assertEqual(result["agent_id"], "ag-1")
        url = mock_open.call_args[0][0].full_url
        self.assertTrue(url.endswith("/agents"), url)

    def test_get_traces_calls_correct_endpoint(self):
        resp = _make_response([{"type": "llm", "name": "fn"}])
        with patch("urllib.request.urlopen", return_value=resp) as mock_open:
            result = self._client().get_traces("ag-1", limit=5)

        self.assertEqual(result[0]["type"], "llm")
        url = mock_open.call_args[0][0].full_url
        self.assertIn("/agents/ag-1/traces", url)

    def test_get_logs_calls_correct_endpoint(self):
        resp = _make_response([{"timestamp": "2024-01-01T00:00:00Z", "message": "hello"}])
        with patch("urllib.request.urlopen", return_value=resp) as mock_open:
            result = self._client().get_logs("ag-1", limit=10)

        self.assertEqual(result[0]["message"], "hello")
        url = mock_open.call_args[0][0].full_url
        self.assertIn("/agents/ag-1/logs", url)

    def test_request_raises_gradient_api_error_on_http_error(self):
        err_body = json.dumps({"message": "Unauthorized"}).encode("utf-8")
        http_err = urllib.error.HTTPError(
            url="https://example.com/v1/agents",
            code=401,
            msg="Unauthorized",
            hdrs={},  # type: ignore[arg-type]
            fp=BytesIO(err_body),
        )
        with patch("urllib.request.urlopen", side_effect=http_err):
            with self.assertRaises(GradientAPIError) as ctx:
                self._client().deploy_agent("x", "agent:entry")

        self.assertEqual(ctx.exception.status, 401)

    def test_bearer_token_sent_in_header(self):
        resp = _make_response({"agent_id": "ag-2", "status": "ok"})
        with patch("urllib.request.urlopen", return_value=resp) as mock_open:
            self._client().deploy_agent("x", "agent:entry")

        req = mock_open.call_args[0][0]
        self.assertEqual(req.get_header("Authorization"), "Bearer test-key")


if __name__ == "__main__":
    unittest.main()
