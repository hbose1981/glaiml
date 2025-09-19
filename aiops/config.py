from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    # API
    api_host: str = os.getenv("AIOPS_API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("AIOPS_API_PORT", "8000"))

    # Prometheus
    prometheus_base_url: str = os.getenv("PROM_BASE_URL", "http://localhost:9090")

    # Postgres (pgvector) for RAG
    pg_host: str = os.getenv("PG_HOST", "localhost")
    pg_port: int = int(os.getenv("PG_PORT", "5432"))
    pg_db: str = os.getenv("PG_DB", "embeddings")
    pg_user: str = os.getenv("PG_USER", "postgres")
    pg_pass: str = os.getenv("PG_PASS", "postgres")
    pg_table: str = os.getenv("PG_RAG_TABLE", "web_embeddings")

    # Embedding model
    embed_model: str = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # ServiceNow (default to local mock)
    snow_instance: str = os.getenv("SNOW_INSTANCE", "http://localhost:8001")
    snow_user: str = os.getenv("SNOW_USER", "")
    snow_pass: str = os.getenv("SNOW_PASS", "")

    # GitLab
    gitlab_base_url: str = os.getenv("GITLAB_BASE_URL", "")
    gitlab_token: str = os.getenv("GITLAB_TOKEN", "")

    # Correlation
    correlation_t_window_secs: int = int(os.getenv("CORRELATION_T_WINDOW_SECS", "600"))

    # Dry-run toggle (reserved)
    dry_run: bool = os.getenv("AIOPS_DRY_RUN", "true").lower() in ("1", "true", "yes")

    # Feature toggles
    disable_rag: bool = os.getenv("AIOPS_DISABLE_RAG", "false").lower() in ("1", "true", "yes")
