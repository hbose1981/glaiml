"""
FastAPI webhook receiver for Alertmanager and simple agent orchestration.
- POST /alert : receives Alertmanager alerts
- GET /health : liveness

This is a minimal scaffold that wires Detection -> Triage and posts a summary
(to console for now). Extend to integrate ServiceNow/GitLab in integrations/.
"""
from __future__ import annotations

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from aiops.core.orchestrator import Orchestrator
from aiops.config import Settings

app = FastAPI(title="AIOps Webhook Receiver")
settings = Settings()
orchestrator = Orchestrator(settings=settings)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/alert")
async def alert_webhook(request: Request):
    payload = await request.json()
    # Alertmanager sends {version, groupKey, status, receiver, groupLabels, commonLabels, commonAnnotations, externalURL, alerts: [...]}
    incident_id = orchestrator.handle_alertmanager_payload(payload)
    return JSONResponse({"ok": True, "incident_id": incident_id})


if __name__ == "__main__":
    host = os.getenv("AIOPS_API_HOST", "0.0.0.0")
    port = int(os.getenv("AIOPS_API_PORT", "8000"))
    uvicorn.run("aiops.api.main:app", host=host, port=port, reload=False)
