from typing import List, Optional
from pydantic import BaseModel, EmailStr
from app.models.base import PyObjectId, DocumentModel
from app.db.collections import db
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class OrgMembership(DocumentModel):
    org_id: PyObjectId
    org_slug: str
    role: UserRole
    created_by: Optional[PyObjectId] = None


# ========== User ==========
class User(DocumentModel):
    email: EmailStr
    full_name: str
    photo_url: Optional[str] = None
    role: UserRole = UserRole.MEMBER
    team_ids: List[PyObjectId] = []
    created_by: Optional[PyObjectId] = None
    org_memberships: List[OrgMembership] = []
    current_org: Optional[OrgMembership] = None

    @classmethod
    def collection(cls):
        return db["users"]
