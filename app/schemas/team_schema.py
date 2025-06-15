from pydantic import BaseModel
from typing import List


class TeamCreate(BaseModel):
    name: str
    org_id: str
    member_ids: List[str] = []
