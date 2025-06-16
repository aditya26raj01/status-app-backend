from typing import Dict, Optional
from app.models.base import PyObjectId, DocumentModel
from app.db.collections import db
from datetime import datetime
from enum import Enum


# Define possible entity types for log entries
class EntityType(str, Enum):
    SERVICE = "Service"
    ORGANIZATION = "Organization"
    INCIDENT = "Incident"
    # Add other entity types as needed


# Define possible change types for log entries
class ChangeType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    # Add other change types as needed


# Model for a log entry
class LogEntry(DocumentModel):
    entity_id: PyObjectId  # ID of the entity being logged
    entity_type: EntityType  # Type of the entity
    change_type: ChangeType  # Type of change made
    changes: Dict[str, Optional[str]]  # Details of the changes made
    org_id: PyObjectId  # ID of the organization

    # Define the MongoDB collection for log entries
    @classmethod
    def collection(cls):
        return db["log_entries"]
