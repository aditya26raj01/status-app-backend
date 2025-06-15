from app.models.base import PyObjectId, DocumentModel
from app.db.collections import db


# ========== StatusLog ==========
class StatusLog(DocumentModel):
    service_id: PyObjectId
    old_status: str
    new_status: str

    @classmethod
    def collection(cls):
        return db["status_logs"]
