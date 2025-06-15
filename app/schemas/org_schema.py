from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str
    domain: str
    org_slug: str
