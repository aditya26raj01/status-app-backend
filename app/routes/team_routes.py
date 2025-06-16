# Import necessary modules and dependencies
# FastAPI components for routing and exceptions
# Custom models and schemas for teams and users
# Authentication dependency
# Typing for type hints

from fastapi import APIRouter, HTTPException
from app.models.base import PyObjectId
from app.models.team_model import Team, TeamMember
from app.schemas.team_schema import TeamCreate
from app.dependencies.auth import get_current_user
from app.models.user_model import User, UserRole
from fastapi import Depends
from typing import List


# Create a router for team-related endpoints with a prefix and tags
router = APIRouter(prefix="/team", tags=["Teams"])


# Endpoint to create a new team
# Accepts team data and the current user as input
# Returns the created team
@router.post("/create-team", response_model=Team)
async def create_team(team_data: TeamCreate, user: User = Depends(get_current_user)):
    # Find all users with the given member IDs
    members = await User.find_all(
        {"_id": {"$in": [PyObjectId(member_id) for member_id in team_data.member_ids]}}
    )
    # Create a new team object from the provided data
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
    # Save the team to the database
    await team.save()
    return team


# Endpoint to list all teams for a given organization
# Accepts organization ID and the current user as input
# Returns a list of teams
@router.get("/get-all-teams", response_model=List[Team])
async def list_teams(org_id: str, user: User = Depends(get_current_user)):
    # Find all teams for the given organization ID
    teams = await Team.find_all(
        {
            "org_id": PyObjectId(org_id),
        }
    )
    # Return the list of teams
    return teams


# Endpoint to fetch a specific team by its ID
# Accepts team ID as input
# Returns the team if found
@router.get("/{team_id}", response_model=Team)
async def fetch_team(team_id: str):
    # Find the team by its ID
    team = await Team.find_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    # Return the team
    return team
