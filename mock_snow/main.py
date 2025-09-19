"""
Mock ServiceNow API using FastAPI.
Endpoints:
- POST /incident : {short_description, description} -> {number}
- POST /incident/{number}/comment : {note}
- GET  /incident/{number}

This is an in-memory mock for local dry runs.
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import uvicorn
import os


app = FastAPI(title="Mock ServiceNow")


class IncidentCreate(BaseModel):
    short_description: str
    description: str | None = None


class Comment(BaseModel):
    note: str


class Incident(BaseModel):
    number: str
    short_description: str
    description: str | None = None
    comments: List[str] = []


_INCIDENTS: Dict[str, Incident] = {}
_COUNTER = 1000


def _next_number() -> str:
    global _COUNTER
    _COUNTER += 1
    return f"INC{_COUNTER}"


@app.post("/incident")
def create_incident(payload: IncidentCreate) -> Dict[str, str]:
    number = _next_number()
    inc = Incident(number=number,
                   short_description=payload.short_description,
                   description=payload.description,
                   comments=[])
    _INCIDENTS[number] = inc
    return {"number": number}


@app.post("/incident/{number}/comment")
def add_comment(number: str, payload: Comment) -> Dict[str, str]:
    inc = _INCIDENTS.get(number)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    inc.comments.append(payload.note)
    return {"ok": "true"}


@app.get("/incident/{number}")
def get_incident(number: str) -> Incident:
    inc = _INCIDENTS.get(number)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc


@app.get("/incidents")
def list_incidents():
    return sorted(_INCIDENTS.keys())


if __name__ == "__main__":
    host = os.getenv("MOCK_SNOW_HOST", "0.0.0.0")
    port = int(os.getenv("MOCK_SNOW_PORT", "8001"))
    uvicorn.run("mock_snow.main:app", host=host, port=port, reload=False)
