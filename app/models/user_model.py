# Import necessary modules
# Typing for type hints
# Pydantic for data validation and settings management
# Base document model and custom ObjectId
# Database collections
# Enum for defining constant values

from typing import List, Optional
from pydantic import BaseModel, EmailStr
from app.models.base import PyObjectId, DocumentModel
from app.db.collections import db
from enum import Enum


# Define possible roles for a user
class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


# Model for an organization membership
class OrgMembership(DocumentModel):
    org_id: PyObjectId  # ID of the organization
    org_slug: str  # Slug for the organization
    role: UserRole  # Role of the user in the organization
    created_by: Optional[PyObjectId] = None  # ID of the creator


# Model for a user
class User(DocumentModel):
    email: EmailStr  # Email of the user
    full_name: str  # Full name of the user
    photo_url: Optional[str] = None  # URL of the user's photo
    role: UserRole = UserRole.MEMBER  # Role of the user
    team_ids: List[PyObjectId] = []  # List of team IDs the user belongs to
    created_by: Optional[PyObjectId] = None  # ID of the creator
    org_memberships: List[OrgMembership] = []  # List of organization memberships
    current_org: Optional[OrgMembership] = None  # Current organization membership

    # Define the MongoDB collection for users
    @classmethod
    def collection(cls):
        return db["users"]
