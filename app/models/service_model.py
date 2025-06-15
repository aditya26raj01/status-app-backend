from typing import Optional
from app.models.base import PyObjectId, DocumentModel
from app.db.collections import db
from enum import Enum


class ServiceStatus(str, Enum):
    OPERATIONAL = "operational"
    DEGRADED_PERFORMANCE = "degraded_performance"
    MAINTENANCE = "maintenance"
    OUTAGE = "outage"
    UNKNOWN = "unknown"


# ========== Service ==========
class Service(DocumentModel):
    name: str
    description: Optional[str] = None
    status: ServiceStatus = ServiceStatus.UNKNOWN
    org_id: PyObjectId

    @classmethod
    def collection(cls):
        return db["services"]
