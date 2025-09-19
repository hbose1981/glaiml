from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time


@dataclass
class Alert:
    status: str
    labels: Dict[str, str]
    annotations: Dict[str, str]
    startsAt: str
    endsAt: Optional[str] = None


@dataclass
class Incident:
    id: str
    status: str
    group_labels: Dict[str, str]
    common_labels: Dict[str, str]
    common_annotations: Dict[str, str]
    alerts: List[Alert]
    created_at: float = field(default_factory=lambda: time.time())
    notes: List[str] = field(default_factory=list)
    suspects: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    hosts: List[str] = field(default_factory=list)
