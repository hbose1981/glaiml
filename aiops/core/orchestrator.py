from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict

from aiops.core.models import Incident, Alert
from aiops.config import Settings
from aiops.agents.detection import DetectionAgent
from aiops.agents.triage import TriageAgent
from aiops.integrations.servicenow import ServiceNowClient


class Orchestrator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.detection = DetectionAgent(settings)
        self.triage = TriageAgent(settings)
        self.snow = ServiceNowClient(
            instance=settings.snow_instance,
            user=settings.snow_user,
            password=settings.snow_pass,
        )

    def _make_incident_id(self, payload: Dict[str, Any]) -> str:
        # Derive a stable ID from Alertmanager groupKey + timestamp
        src = f"{payload.get('groupKey','')}:{int(time.time())}"
        return hashlib.sha1(src.encode()).hexdigest()[:12]

    def handle_alertmanager_payload(self, payload: Dict[str, Any]) -> str:
        # Parse into Incident
        alerts = [
            Alert(
                status=a.get("status", ""),
                labels=a.get("labels", {}),
                annotations=a.get("annotations", {}),
                startsAt=a.get("startsAt", ""),
                endsAt=a.get("endsAt"),
            )
            for a in payload.get("alerts", [])
        ]
        incident = Incident(
            id=self._make_incident_id(payload),
            status=payload.get("status", "firing"),
            group_labels=payload.get("groupLabels", {}),
            common_labels=payload.get("commonLabels", {}),
            common_annotations=payload.get("commonAnnotations", {}),
            alerts=alerts,
        )

        # Detection / correlation
        self.detection.enrich_incident(incident)

        # Triage
        self.triage.enrich_incident(incident)

        # Prepare summary
        summary = {
            "incident_id": incident.id,
            "status": incident.status,
            "services": incident.services,
            "hosts": incident.hosts,
            "notes": incident.notes,
            "suspects": incident.suspects,
        }
        summary_txt = json.dumps(summary, indent=2)
        print("[AIOPS] Incident summary:\n" + summary_txt)

        # ServiceNow (mock or real): create incident and append comment
        number = self.snow.create_incident(
            short_description=f"AIOps incident {incident.id}",
            description=f"Grouped alerts for services={incident.services} hosts={incident.hosts}",
        )
        if number:
            self.snow.add_comment(number, f"AIOps enrichment:\n{summary_txt}")
        return incident.id
