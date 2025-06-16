# Import necessary modules
# Base document model
# Database collections

from app.models.base import DocumentModel
from app.db.collections import db


# ========== Organization ==========
# Model for an organization
class Organization(DocumentModel):
    name: str  # Name of the organization
    domain: str  # Domain of the organization
    org_slug: str  # Slug for the organization
    created_by_username: str  # Username of the creator

    # Define the MongoDB collection for organizations
    @classmethod
    def collection(cls):
        return db["orgs"]
