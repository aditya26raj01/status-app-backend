from pydantic import BaseModel
from typing import List, Optional
from app.models.incident_model import (
    AffectedService,
    IncidentStatus,
    IncidentSeverity,
    IncidentUpdate,
)
from datetime import datetime
from app.models.service_model import ServiceStatus


class AffectedServiceUpdate(BaseModel):
    service_id: str
    status: ServiceStatus
    created_at: datetime


class IncidentUpdateCreate(BaseModel):
    message: str
    created_by: str
    created_at: datetime


class IncidentCreate(BaseModel):
    title: str
    description: str
    status: IncidentStatus
    severity: Optional[IncidentSeverity]
    affected_services: Optional[List[AffectedService]]
    org_id: str
    started_at: datetime
    resolved_at: Optional[datetime]
    updates: Optional[List[IncidentUpdate]]


class UpdateIncident(IncidentCreate):
    incident_id: str
    affected_services: Optional[List[AffectedServiceUpdate]]
    updates: Optional[List[IncidentUpdateCreate]]
