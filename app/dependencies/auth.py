# Import necessary modules
# FastAPI components for handling requests and exceptions
# Typing for type hints

from fastapi import Request, HTTPException, Depends
from typing import List


# Function to get the current user from the request state
# Raises an HTTPException if the user is not found
def get_current_user(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


# Function to create a role checker dependency
# Accepts a list of allowed roles
# Returns a checker function that verifies the user's role
def require_roles(allowed_roles: List[str]):
    def checker(user=Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden: Insufficient role")
        return user

    return checker

    # Check if the user's role is in the allowed roles
    # Raise an HTTPException if not

    # Return the user if the role is sufficient
