from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List

import httpx


class PrometheusClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def query_range(self, query: str, start: dt.datetime, end: dt.datetime, step_seconds: int) -> List[Dict[str, Any]]:
        params = {
            "query": query,
            "start": start.isoformat() + "Z",
            "end": end.isoformat() + "Z",
            "step": str(step_seconds),
        }
        url = f"{self.base_url}/api/v1/query_range"
        r = httpx.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "success":
            return []
        result = data.get("data", {}).get("result", [])
        return result
