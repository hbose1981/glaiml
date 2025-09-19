from __future__ import annotations

from typing import List

from aiops.core.models import Incident
from aiops.config import Settings


class DetectionAgent:
    """Basic detection/correlation that extracts hosts/services from alert labels
    and applies a simple time-window grouping heuristic (placeholder).
    """

    def __init__(self, settings: Settings):
        self.settings = settings

    def enrich_incident(self, incident: Incident) -> None:
        services: List[str] = []
        hosts: List[str] = []
        for a in incident.alerts:
            svc = a.labels.get("service") or a.labels.get("job") or a.labels.get("app")
            host = a.labels.get("instance") or a.labels.get("host")
            if svc and svc not in services:
                services.append(svc)
            if host and host not in hosts:
                hosts.append(host)
        incident.services = services
        incident.hosts = hosts
        incident.notes.append(
            f"Detection: grouped {len(incident.alerts)} alerts | services={services} hosts={hosts}"
        )
