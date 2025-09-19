# AIOps PoC Scaffold

This is a minimal, agentic AIOps scaffold tailored for VM environments with Prometheus (or Elastic), GitLab CI/CD, and ServiceNow. It operates Human-in-the-Loop (HITL): agents propose; humans approve and execute via GitLab and/or ServiceNow.

## Directory Structure

```
aiops/
  api/
    main.py                 # FastAPI webhook receiver (/alert) and health
  agents/
    detection.py            # Extracts services/hosts from alerts
    triage.py               # Prometheus queries + RAG (pgvector) enrichment
  core/
    models.py               # Alert/Incident models
    orchestrator.py         # Orchestrates Detection -> Triage (extend with RCA/Remediation)
  integrations/
    prometheus.py           # Range queries to Prometheus
    rag_pgvector.py         # RAG search using pgvector + sentence-transformers
    servicenow.py           # Placeholder client
  config.py                 # Environment-based settings
```

## Quick Start

1) Ensure dependencies

```bash
pip install -r requirements.txt
```

2) Ensure pgvector is running (you already have docker-compose in repo)

3) Run the API

```bash
python -m aiops.api.main
```

It starts FastAPI on `AIOPS_API_HOST`:`AIOPS_API_PORT` (defaults 0.0.0.0:8000). Health endpoint: `GET /health`.

4) Point Alertmanager webhook to the API

In your Alertmanager config:

```yaml
route:
  receiver: aiops-webhook
receivers:
  - name: aiops-webhook
    webhook_configs:
      - url: http://host.docker.internal:8000/alert
```

5) RAG Requirements

- The RAG client uses your existing pgvector table populated by scripts like `html_to_pgvector.py`.
- Configure env vars (or `.env`) to point at your Postgres and table:

```env
PG_HOST=localhost
PG_PORT=5432
PG_DB=embeddings
PG_USER=postgres
PG_PASS=postgres
PG_RAG_TABLE=web_embeddings
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
PROM_BASE_URL=http://localhost:9090
```

## Local Demo (no Compose)

Use these steps to run everything locally for a quick demo:

1) Start Mock ServiceNow (local FastAPI)

```bash
python -m mock_snow.main
```

2) Start the AIOps API (local FastAPI)

```bash
python -m aiops.api.main
```

3) Start Prometheus (Docker) and node_exporter (Docker)

```bash
# Prometheus UI: http://localhost:9090
docker run --name aiops-prom -d -p 9090:9090 \
  -v ${PWD}/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus:latest --config.file=/etc/prometheus/prometheus.yml

# Node exporter metrics: http://localhost:9100/metrics
docker run --name node-exporter -d -p 9100:9100 prom/node-exporter:latest
```

Prometheus config lives at `prometheus/prometheus.yml` and includes:
- `prometheus` job: `localhost:9090`
- `node` job: tries `host.docker.internal:9100` and `localhost:9100`

4) Send a sample Alertmanager payload

PowerShell execution policies may block `scripts/send_sample_alert.ps1`. Use Python or curl as alternatives:

```bash
# Python (httpx) with higher timeout (Windows/Linux/macOS)
python -c "import httpx,json; payload={'version':'4','groupKey':'example-group','status':'firing','receiver':'aiops-webhook','groupLabels':{'alertname':'HighCPU'},'commonLabels':{'severity':'warning','service':'node','instance':'vm-001:9100','job':'node'},'commonAnnotations':{'summary':'CPU usage high'},'externalURL':'http://alertmanager.local','alerts':[{'status':'firing','labels':{'alertname':'HighCPU','severity':'warning','service':'node','instance':'vm-001:9100','job':'node'},'annotations':{'summary':'CPU load above threshold'},'startsAt':'2025-01-01T00:00:00Z','endsAt':'','generatorURL':'http://prometheus.local'}]}; r=httpx.post('http://localhost:8000/alert', json=payload, timeout=120); print(r.status_code); print(r.text)"

# curl (Windows ships with curl.exe)
curl -X POST http://localhost:8000/alert -H "Content-Type: application/json" -d "{\"version\":\"4\",\"groupKey\":\"example-group\",\"status\":\"firing\",\"receiver\":\"aiops-webhook\",\"groupLabels\":{\"alertname\":\"HighCPU\"},\"commonLabels\":{\"severity\":\"warning\",\"service\":\"node\",\"instance\":\"vm-001:9100\",\"job\":\"node\"},\"commonAnnotations\":{\"summary\":\"CPU usage high\"},\"externalURL\":\"http://alertmanager.local\",\"alerts\":[{\"status\":\"firing\",\"labels\":{\"alertname\":\"HighCPU\",\"severity\":\"warning\",\"service\":\"node\",\"instance\":\"vm-001:9100\",\"job\":\"node\"},\"annotations\":{\"summary\":\"CPU load above threshold\"},\"startsAt\":\"2025-01-01T00:00:00Z\",\"endsAt\":\"\",\"generatorURL\":\"http://prometheus.local\"}]}"
```

## What Happens on /alert

- Parses Alertmanager payload
- Detection: extracts `service/job/app` and `instance/host` labels
- Triage: runs a Prometheus range query (`up{job="<svc>"}`) for last 30 minutes and retrieves related runbook snippets via RAG
- Prints a structured incident summary to console (replace with ServiceNow notes)

## Next Steps (Where your help is needed)

- Provide or confirm:
  - **Service label convention** in alerts (`service`, `job`, or `app`) and **host label** (`instance` or `host`). This improves correlation.
  - **Prometheus URL** (PROM_BASE_URL) for range queries.
  - **Postgres connection** details for pgvector (already used in this repo).
  - **ServiceNow**: instance URL and credentials (if you want the bot to auto-append notes to incidents).
  - **GitLab**: base URL and token if you want the remediation planner to open MRs/pipelines for HITL.

- Prioritized features to add next:
  - RCA Agent: time-series change point and (optional) Elastic error clustering
  - Remediation Planner: generate GitLab job YAML with safe actions (restart service on VM, revert config)
  - ServiceNow integration: draft incident update and change approval tasks
  - Correlation Graph: simple service<->host mapping from your VM inventory

## Environment Variables (aiops/config.py)

```
AIOPS_API_HOST=0.0.0.0
AIOPS_API_PORT=8000
PROM_BASE_URL=http://localhost:9090
PG_HOST=localhost
PG_PORT=5432
PG_DB=embeddings
PG_USER=postgres
PG_PASS=postgres
PG_RAG_TABLE=web_embeddings
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
SNOW_INSTANCE=
SNOW_USER=
SNOW_PASS=
GITLAB_BASE_URL=
GITLAB_TOKEN=
CORRELATION_T_WINDOW_SECS=600
AIOPS_DISABLE_RAG=false
```

## Notes

- Human-in-the-Loop: no remediation is executed automatically; everything is proposed and requires approval.
- Minimal error handling/logging for PoC; productionize with structured logs, retries, and telemetry.
- If you prefer Elastic instead of Prometheus, we can add a simple logs client and error pattern clustering.

## Feature Toggles

- `AIOPS_DISABLE_RAG`: when `true`, triage will skip pgvector RAG lookups and add a note "RAG disabled by configuration". Useful for fast demos or when embeddings DB/model is unavailable.

## Session Notes

See `SESSION_NOTES_2025-09-20.txt` for a concrete run log, commands used, and suggested next steps.
