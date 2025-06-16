from typing import List, Optional
from app.models.base import PyObjectId, DocumentModel
from app.db.collections import db
from app.models.user_model import UserRole


class TeamMember(DocumentModel):
    user_id: PyObjectId
    user_name: str
    user_email: str
    role: UserRole
    created_by: Optional[PyObjectId] = None


# ========== Team ==========
class Team(DocumentModel):
    name: str
    org_id: PyObjectId
    members: List[TeamMember] = []

    @classmethod
    def collection(cls):
        return db["teams"]
