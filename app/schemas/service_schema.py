from pydantic import BaseModel
from app.models.service_model import ServiceStatus


class ServiceCreate(BaseModel):
    name: str
    description: str
    status: ServiceStatus
    org_id: str


class ServiceUpdate(ServiceCreate):
    service_id: str
