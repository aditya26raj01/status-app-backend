from typing import Optional, List
from datetime import datetime
from pydantic import Field
from app.models.base import DocumentModel, PyObjectId
from app.db.collections import db
from enum import Enum
from app.models.service_model import ServiceStatus


class IncidentStatus(str, Enum):
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"


class IncidentSeverity(str, Enum):
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class IncidentUpdate(DocumentModel):
    message: str
    created_by: Optional[PyObjectId] = None


class AffectedService(DocumentModel):
    service_id: PyObjectId
    status: ServiceStatus = ServiceStatus.UNKNOWN
    created_by: Optional[PyObjectId] = None


# ========== Incident ==========
class Incident(DocumentModel):
    title: str
    description: str
    status: IncidentStatus
    severity: Optional[IncidentSeverity] = None
    affected_services: List[AffectedService] = []
    org_id: PyObjectId
    started_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    updates: Optional[List[IncidentUpdate]] = []

    @classmethod
    def collection(cls):
        return db["incidents"]
