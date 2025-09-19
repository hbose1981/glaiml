from __future__ import annotations

from typing import List, Tuple

import psycopg2
from sentence_transformers import SentenceTransformer

from aiops.config import Settings


def _to_vector_literal(vec):
    return "[" + ", ".join(f"{x:.8f}" for x in vec) + "]"


class RagClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = SentenceTransformer(settings.embed_model)

    def _conn(self):
        return psycopg2.connect(
            host=self.settings.pg_host,
            port=self.settings.pg_port,
            dbname=self.settings.pg_db,
            user=self.settings.pg_user,
            password=self.settings.pg_pass,
        )

    def search(self, query_text: str, top_k: int = 3) -> List[Tuple[str, float, str]]:
        # Returns normalized embeddings for stable cosine similarity
        vec = self.model.encode(query_text, convert_to_numpy=True, normalize_embeddings=True).tolist()
        vec_lit = _to_vector_literal(vec)
        sql = f"""
        WITH q AS (SELECT %s::vector AS v)
        SELECT content, (1 - cosine_distance(embedding, q.v)) AS similarity, url
        FROM {self.settings.pg_table}, q
        ORDER BY cosine_distance(embedding, q.v) ASC
        LIMIT %s
        """
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (vec_lit, top_k))
                rows = cur.fetchall()
                return [(r[0], float(r[1]), r[2]) for r in rows]
