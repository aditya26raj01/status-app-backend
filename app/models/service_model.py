# Import necessary modules
# Typing for type hints
# Base document model and custom ObjectId
# Database collections
# Enum for defining constant values

from typing import Optional
from app.models.base import PyObjectId, DocumentModel
from app.db.collections import db
from enum import Enum


# Define possible statuses for a service
class ServiceStatus(str, Enum):
    OPERATIONAL = "operational"
    DEGRADED_PERFORMANCE = "degraded_performance"
    MAINTENANCE = "maintenance"
    OUTAGE = "outage"
    UNKNOWN = "unknown"


# Model for a service
class Service(DocumentModel):
    name: str  # Name of the service
    description: Optional[str] = None  # Description of the service
    status: ServiceStatus = ServiceStatus.UNKNOWN  # Current status of the service
    org_id: PyObjectId  # ID of the organization
    created_by_username: str  # Username of the creator

    # Define the MongoDB collection for services
    @classmethod
    def collection(cls):
        return db["services"]
