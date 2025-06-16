# Import necessary modules
# FastAPI components for handling requests and exceptions
# Starlette middleware and responses for HTTP handling
# Firebase Admin SDK for token verification
# Custom user model

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from firebase_admin import auth as firebase_auth
from firebase_admin._auth_utils import InvalidIdTokenError
from app.models.user_model import User
from fastapi import HTTPException


# Define a middleware class for Firebase authentication
class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for the get-org-by-domain endpoint
        # If the request URL path starts with '/org/get-org-by-domain', bypass authentication
        if request.url.path.startswith("/org/get-org-by-domain"):
            return await call_next(request)
        # Skip authentication for the sync-user-to-db endpoint
        # If the request URL path starts with '/user/sync-user-to-db', bypass authentication
        if request.url.path.startswith("/user/sync-user-to-db"):
            return await call_next(request)
        # Skip authentication for the get-org-status endpoint
        # If the request URL path starts with '/status/get-org-status', bypass authentication
        if request.url.path.startswith("/status/get-org-status"):
            return await call_next(request)
        # Get the Authorization header from the request
        auth_header = request.headers.get("Authorization")
        # Return an unauthorized response if the header is missing or does not start with 'Bearer '
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"detail": "Unauthorized: Missing or invalid token"}, status_code=401
            )

        # Extract the token from the Authorization header
        token = auth_header.split(" ")[1]
        try:
            # Verify the token using Firebase Admin SDK
            decoded_token = firebase_auth.verify_id_token(token)
            # Retrieve the user's email from the decoded token
            email = decoded_token["email"]
            # Find the user in the database by email
            user = await User.collection().find_one({"email": email})
            # Raise an HTTPException if the user is not found
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            # Set the user in the request state for downstream use
            request.state.user = User(**user)
        except (InvalidIdTokenError, KeyError):
            # Handle invalid or expired tokens
            # Return an unauthorized response
            return JSONResponse(
                {"detail": "Unauthorized: Invalid or expired token"}, status_code=401
            )
        except Exception:
            # Handle any other exceptions
            # Return a generic unauthorized response
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)

        # Proceed with the request if authentication is successful
        return await call_next(request)
