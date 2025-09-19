from __future__ import annotations

import datetime as dt
from typing import List

from aiops.core.models import Incident
from aiops.config import Settings
from aiops.integrations.prometheus import PrometheusClient
from aiops.integrations.rag_pgvector import RagClient


class TriageAgent:
    """Enrich incidents with quick telemetry context and relevant knowledge snippets."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.prom = PrometheusClient(base_url=settings.prometheus_base_url)
        # Lazy-init RAG to avoid model download at API startup
        self.rag = None  # type: ignore

    def _get_rag(self):
        if self.rag is not None:
            return self.rag
        try:
            self.rag = RagClient(self.settings)
        except Exception:
            # Leave as None if initialization fails
            self.rag = None
        return self.rag

    def enrich_incident(self, incident: Incident) -> None:
        # Time window: last 30 minutes
        end = dt.datetime.utcnow()
        start = end - dt.timedelta(minutes=30)
        step = 60  # 1 minute resolution

        # For each service, pull a simple CPU or error rate panel if possible
        for svc in incident.services or ["unknown"]:
            # Example query: up{job="<svc>"}
            query = f'up{{job="{svc}"}}'
            try:
                series = self.prom.query_range(query, start, end, step)
                if series:
                    incident.notes.append(
                        f"Triage: Prometheus query '{query}' returned {len(series)} series over last 30m."
                    )
                else:
                    incident.notes.append(
                        f"Triage: Prometheus query '{query}' returned no data."
                    )
            except Exception as e:
                incident.notes.append(f"Triage: Prometheus error: {e}")

            # RAG: fetch relevant runbooks/docs
            if self.settings.disable_rag:
                incident.notes.append("Triage: RAG disabled by configuration (AIOPS_DISABLE_RAG).")
            else:
                rag = self._get_rag()
                if rag is None:
                    incident.notes.append("Triage: RAG disabled or not initialized.")
                else:
                    try:
                        chunks = rag.search(query_text=f"service {svc} incident runbook", top_k=3)
                        if chunks:
                            incident.notes.append("Triage: Relevant runbook snippets:")
                            for i, (content, score, url) in enumerate(chunks, 1):
                                preview = content[:180].replace("\n", " ")
                                incident.notes.append(f"  {i}. score={score:.4f} url={url} | {preview}")
                        else:
                            incident.notes.append("Triage: No RAG results.")
                    except Exception as e:
                        incident.notes.append(f"Triage: RAG error: {e}")

        if not incident.services:
            # also try RAG based on common labels
            hints = " ".join([f"{k}:{v}" for k, v in (incident.common_labels or {}).items()])
            if not self.settings.disable_rag:
                rag = self._get_rag()
                if rag is not None:
                    try:
                        chunks = rag.search(query_text=f"incident {hints}", top_k=3)
                        if chunks:
                            incident.notes.append("Triage: Relevant docs from labels:")
                            for i, (content, score, url) in enumerate(chunks, 1):
                                preview = content[:180].replace("\n", " ")
                                incident.notes.append(f"  {i}. score={score:.4f} url={url} | {preview}")
                    except Exception as e:
                        incident.notes.append(f"Triage: RAG error: {e}")
