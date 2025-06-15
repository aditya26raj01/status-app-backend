from app.models.base import DocumentModel
from app.db.collections import db


# ========== Organization ==========
class Organization(DocumentModel):
    name: str
    domain: str
    org_slug: str
    is_admin_org: bool = False

    @classmethod
    def collection(cls):
        return db["orgs"]
