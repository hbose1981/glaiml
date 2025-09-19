"""
ServiceNow integration (supports mock ServiceNow running locally).

If `instance` is like http://localhost:8001 (mock_snow), this client will call:
  - POST /incident {short_description, description} -> {number}
  - POST /incident/{number}/comment {note}

If not configured, methods are no-ops with console prints.
"""
from __future__ import annotations

from typing import Optional

import httpx


class ServiceNowClient:
    def __init__(self, instance: str, user: str, password: str):
        self.instance = instance.rstrip("/") if instance else ""
        self.user = user
        self.password = password

    def enabled(self) -> bool:
        # For mock, we don't require creds; if real SNOW, you can enforce auth.
        return bool(self.instance)

    def create_incident(self, short_description: str, description: str = "") -> Optional[str]:
        if not self.enabled():
            print("[ServiceNow] Skipped create (not configured)")
            return None
        url = f"{self.instance}/incident"
        try:
            r = httpx.post(url, json={"short_description": short_description, "description": description}, timeout=10)
            r.raise_for_status()
            number = r.json().get("number")
            print(f"[ServiceNow] Created incident {number}")
            return number
        except Exception as e:
            print(f"[ServiceNow] Create incident failed: {e}")
            return None

    def add_comment(self, incident_number: str, note: str) -> bool:
        if not (self.enabled() and incident_number):
            print("[ServiceNow] Skipped comment (not configured)")
            return False
        url = f"{self.instance}/incident/{incident_number}/comment"
        try:
            r = httpx.post(url, json={"note": note}, timeout=10)
            r.raise_for_status()
            print(f"[ServiceNow] Appended comment to {incident_number}")
            return True
        except Exception as e:
            print(f"[ServiceNow] Add comment failed: {e}")
            return False
