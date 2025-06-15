from typing import Dict, Optional
from app.models.base import PyObjectId, DocumentModel
from app.db.collections import db
from datetime import datetime
from enum import Enum


class EntityType(str, Enum):
    SERVICE = "Service"
    ORGANIZATION = "Organization"
    INCIDENT = "Incident"
    # Add other entity types as needed


class ChangeType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    # Add other change types as needed


# ========== LogEntry ==========
class LogEntry(DocumentModel):
    entity_id: PyObjectId
    entity_type: EntityType
    change_type: ChangeType
    changes: Dict[str, Optional[str]]
    org_id: PyObjectId  # Add org_id as a mandatory field

    @classmethod
    def collection(cls):
        return db["log_entries"]
