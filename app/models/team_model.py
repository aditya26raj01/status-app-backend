from typing import List
from app.models.base import PyObjectId, DocumentModel
from app.db.collections import db


# ========== Team ==========
class Team(DocumentModel):
    name: str
    org_id: PyObjectId
    member_ids: List[PyObjectId] = []

    @classmethod
    def collection(cls):
        return db["teams"]
