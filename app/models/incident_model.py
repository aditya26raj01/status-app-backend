from typing import Optional, List
from datetime import datetime
from pydantic import Field
from app.models.base import DocumentModel, PyObjectId
from app.db.collections import db
from enum import Enum
from app.models.service_model import ServiceStatus


# Define possible statuses for an incident
class IncidentStatus(str, Enum):
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"


# Define possible severity levels for an incident
class IncidentSeverity(str, Enum):
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


# Model for updates related to an incident
class IncidentUpdate(DocumentModel):
    message: str  # Update message
    created_by_username: Optional[str] = None  # Username of the creator
    created_by: Optional[PyObjectId] = None  # ID of the creator


# Model for services affected by an incident
class AffectedService(DocumentModel):
    service_id: PyObjectId  # ID of the affected service
    service_name: str  # Name of the affected service
    status: ServiceStatus = ServiceStatus.UNKNOWN  # Status of the service
    created_by: Optional[PyObjectId] = None  # ID of the creator


# Model for an incident
class Incident(DocumentModel):
    title: str  # Title of the incident
    description: str  # Description of the incident
    status: IncidentStatus  # Current status of the incident
    severity: Optional[IncidentSeverity] = None  # Severity level of the incident
    affected_services: List[AffectedService] = []  # List of affected services
    org_id: PyObjectId  # ID of the organization
    started_at: datetime = Field(default_factory=datetime.utcnow)  # Start time
    resolved_at: Optional[datetime] = None  # Resolution time
    updates: Optional[List[IncidentUpdate]] = []  # List of updates
    created_by_username: str  # Username of the creator

    # Define the MongoDB collection for incidents
    @classmethod
    def collection(cls):
        return db["incidents"]
