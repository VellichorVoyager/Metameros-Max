"""Zero-dependency HTTP client for the Gradient AI platform API."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .config import DEFAULT_API_BASE


class GradientAPIError(Exception):
    """Raised when the Gradient API returns a non-2xx response."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(f"HTTP {status}: {message}")
        self.status = status


class GradientClient:
    """Thin wrapper around the Gradient platform REST API.

    Parameters
    ----------
    api_key:
        The Model Access Key (Bearer token).
    api_base:
        Root URL of the Gradient API.  Override this to point at a
        self-hosted or staging endpoint.
    """

    def __init__(
        self,
        api_key: str,
        api_base: str = DEFAULT_API_BASE,
    ) -> None:
        self.api_key = api_key
        self.api_base = api_base.rstrip("/")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.api_base}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(req) as resp:  # noqa: S310
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            try:
                detail = json.loads(exc.read().decode("utf-8"))
                msg = detail.get("message") or detail.get("error") or str(exc)
            except Exception:
                msg = str(exc)
            raise GradientAPIError(exc.code, msg) from exc

    # ------------------------------------------------------------------
    # Public API surface
    # ------------------------------------------------------------------

    def deploy_agent(
        self,
        name: str,
        module: str,
        region: str = "nyc3",
    ) -> dict[str, Any]:
        """Create (or re-deploy) an agent on the Gradient platform.

        Returns the API response which includes ``agent_id`` and ``status``.
        """
        return self._request(
            "POST",
            "/agents",
            {"name": name, "module": module, "region": region},
        )

    def get_traces(
        self,
        agent_id: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Fetch the most recent trace events for *agent_id*."""
        qs = urllib.parse.urlencode({"limit": limit})
        return self._request("GET", f"/agents/{agent_id}/traces?{qs}")

    def get_logs(
        self,
        agent_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Fetch the most recent log lines for *agent_id*."""
        qs = urllib.parse.urlencode({"limit": limit})
        return self._request("GET", f"/agents/{agent_id}/logs?{qs}")
