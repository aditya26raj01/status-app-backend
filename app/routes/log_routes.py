# Import necessary modules and dependencies
# FastAPI components for routing and exceptions
# Custom models for logs and users
# Authentication dependency
# Typing for type hints

from fastapi import APIRouter, HTTPException
from app.models.log_model import LogEntry, PyObjectId
from typing import List
from app.models.user_model import User
from app.dependencies.auth import get_current_user
from fastapi import Depends


# Create a router for log-related endpoints with a prefix and tags
router = APIRouter(prefix="/log", tags=["Logs"])


# Endpoint to list all logs
# Returns a list of all log entries
@router.get("/get-all-logs", response_model=List[LogEntry])
async def list_logs():
    logs = await LogEntry.find_all()
    return logs


# Endpoint to get logs by organization
# Accepts organization ID and the current user as input
# Returns a list of log entries for the specified organization
@router.get("/get-logs-by-org", response_model=List[LogEntry])
async def get_logs_by_org(org_id: str, user: User = Depends(get_current_user)):
    if not user.current_org or str(user.current_org.org_id) != org_id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to view logs for this organization",
        )
    logs = await LogEntry.find_all({"org_id": PyObjectId(org_id)})
    return logs
