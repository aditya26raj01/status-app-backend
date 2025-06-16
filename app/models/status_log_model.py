from app.models.base import PyObjectId, DocumentModel
from app.db.collections import db


# ========== StatusLog ==========
# Model for a status log entry
class StatusLog(DocumentModel):
    service_id: PyObjectId  # ID of the service
    old_status: str  # Previous status of the service
    new_status: str  # New status of the service

    # Define the MongoDB collection for status logs
    @classmethod
    def collection(cls):
        return db["status_logs"]
