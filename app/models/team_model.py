from typing import List, Optional
from app.models.base import PyObjectId, DocumentModel
from app.db.collections import db
from app.models.user_model import UserRole


# Model for a team member
class TeamMember(DocumentModel):
    user_id: PyObjectId  # ID of the user
    user_name: str  # Name of the user
    user_email: str  # Email of the user
    role: UserRole  # Role of the user in the team
    created_by: Optional[PyObjectId] = None  # ID of the creator


# ========== Team ==========
class Team(DocumentModel):
    name: str  # Name of the team
    org_id: PyObjectId  # ID of the organization
    members: List[TeamMember] = []  # List of team members

    # Define the MongoDB collection for teams
    @classmethod
    def collection(cls):
        return db["teams"]
