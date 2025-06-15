from fastapi import APIRouter, HTTPException
from app.models.base import PyObjectId
from app.models.team_model import Team
from app.schemas.team_schema import TeamCreate
from app.dependencies.auth import get_current_user
from app.models.user_model import User
from fastapi import Depends


router = APIRouter(prefix="/team", tags=["Teams"])


@router.post("/", response_model=Team)
async def create_team(team_data: TeamCreate, user: User = Depends(get_current_user)):
    team = Team(
        name=team_data.name,
        org_id=PyObjectId(team_data.org_id),
        member_ids=[PyObjectId(member_id) for member_id in team_data.member_ids],
        created_by=user.id,  # type: ignore
        # because if code reaches here, user is not None
    )
    await team.save()
    return team


@router.get("/{team_id}", response_model=Team)
async def fetch_team(team_id: str):
    team = await Team.find_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team
