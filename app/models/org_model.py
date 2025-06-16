from app.models.base import DocumentModel
from app.db.collections import db


# ========== Organization ==========
class Organization(DocumentModel):
    name: str
    domain: str
    org_slug: str
    created_by_username: str

    @classmethod
    def collection(cls):
        return db["orgs"]
