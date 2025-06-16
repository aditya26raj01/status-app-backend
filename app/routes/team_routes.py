from fastapi import APIRouter, HTTPException
from app.models.base import PyObjectId
from app.models.team_model import Team, TeamMember
from app.schemas.team_schema import TeamCreate
from app.dependencies.auth import get_current_user
from app.models.user_model import User, UserRole
from fastapi import Depends
from typing import List


router = APIRouter(prefix="/team", tags=["Teams"])


@router.post("/create-team", response_model=Team)
async def create_team(team_data: TeamCreate, user: User = Depends(get_current_user)):
    members = await User.find_all(
        {"_id": {"$in": [PyObjectId(member_id) for member_id in team_data.member_ids]}}
    )
    team = Team(
        name=team_data.name,
        org_id=PyObjectId(team_data.org_id),
        members=[
            TeamMember(
                user_id=member.id,  # type: ignore
                user_name=member.full_name,
                role=UserRole.MEMBER,
                user_email=member.email,
            )
            for member in members
        ],
        created_by=user.id,  # type: ignore
        # because if code reaches here, user is not None
    )
    await team.save()
    return team


@router.get("/get-all-teams", response_model=List[Team])
async def list_teams(org_id: str, user: User = Depends(get_current_user)):
    teams = await Team.find_all(
        {
            "org_id": PyObjectId(org_id),
        }
    )
    return teams


@router.get("/{team_id}", response_model=Team)
async def fetch_team(team_id: str):
    team = await Team.find_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team
