# Project Checklist

## Completed ✅

- [x] FastAPI webhook and health endpoints (`aiops/api/main.py`)
- [x] Orchestration: Detection → Triage → ServiceNow (`aiops/core/orchestrator.py`)
- [x] Detection agent extracts `service/job/app` and `instance/host` (`aiops/agents/detection.py`)
- [x] Triage agent:
  - [x] Prometheus range query `up{job="<svc>"}` over last 30m (`aiops/agents/triage.py`)
  - [x] RAG via pgvector with lazy-load model init (`aiops/agents/triage.py`, `aiops/integrations/rag_pgvector.py`)
  - [x] Feature toggle to disable RAG: `AIOPS_DISABLE_RAG` (`aiops/config.py`)
- [x] Integrations:
  - [x] Prometheus client (`aiops/integrations/prometheus.py`)
  - [x] ServiceNow client with mock support (`aiops/integrations/servicenow.py`)
- [x] Mock ServiceNow server (create/comment/list) (`mock_snow/main.py`)
- [x] Prometheus + node_exporter demo:
  - [x] Prometheus config at `prometheus/prometheus.yml` (self + node jobs)
  - [x] Prometheus container `aiops-prom` and node_exporter container
- [x] Sample alert senders:
  - [x] PowerShell script (may be blocked by policy) (`scripts/send_sample_alert.ps1`)
  - [x] README includes Python and curl alternatives
- [x] Documentation updates:
  - [x] Expanded README with local demo steps, feature toggles, and commands
  - [x] Session notes `SESSION_NOTES_2025-09-20.txt`

## Pending / Next 🔜

- [ ] RAG data readiness
  - [ ] Provision Postgres+pgvector with populated embeddings table (`PG_RAG_TABLE`)
  - [ ] Add/confirm ingestion pipeline for docs/runbooks (scripts not included yet)
  - [ ] Optional: connection retries, timeouts, and error surfaces

- [ ] Prometheus telemetry enrichment
  - [ ] Add scrape targets for real services/VMs beyond node_exporter
  - [ ] Configurable Prometheus request timeouts/retries; auth/SSL support if needed

- [ ] ServiceNow (real instance)
  - [ ] Configure real instance URL/creds; add auth handling
  - [ ] Improve note formatting and structure (tables, sections)
  - [ ] Retries/backoff for create/comment

- [ ] RCA and Remediation
  - [ ] RCA agent (e.g., change point detection, error clustering)
  - [ ] Remediation planner (GitLab MR/pipeline drafts) and GitLab integration

- [ ] Reliability and Ops
  - [ ] Structured logging & correlation IDs
  - [ ] Error handling, retries, idempotency
  - [ ] Secrets management and input validation for `/alert`
  - [ ] Rate limiting or signature verification for the webhook

- [ ] Developer Experience
  - [ ] Unit/integration tests for agents and orchestrator
  - [ ] CI pipeline (GitLab CI) and linters
  - [ ] README sections for RAG setup, Prometheus targets, ServiceNow (real) config

## Quick Tips

- Disable RAG for fast demos:
  - Windows PowerShell: `$env:AIOPS_DISABLE_RAG="true"; python -m aiops.api.main`
  - Linux/macOS: `AIOPS_DISABLE_RAG=true python -m aiops.api.main`

- Prometheus UI: http://localhost:9090 (Targets: `prometheus` and `node` should be UP)
- Mock ServiceNow: http://localhost:8001 (GET `/incidents` to list)
