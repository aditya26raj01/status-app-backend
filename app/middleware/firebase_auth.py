from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from firebase_admin import auth as firebase_auth
from firebase_admin._auth_utils import InvalidIdTokenError
from app.models.user_model import User
from fastapi import HTTPException


class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for the get-org-by-domain endpoint
        if request.url.path.startswith("/org/get-org-by-domain"):
            return await call_next(request)
        # Skip authentication for the sync-user-to-db endpoint
        if request.url.path.startswith("/user/sync-user-to-db"):
            return await call_next(request)
        # Skip authentication for the get-org-status endpoint
        if request.url.path.startswith("/status/get-org-status"):
            return await call_next(request)
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"detail": "Unauthorized: Missing or invalid token"}, status_code=401
            )

        token = auth_header.split(" ")[1]
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            email = decoded_token["email"]
            user = await User.collection().find_one({"email": email})
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            # Extract fields from token
            request.state.user = User(**user)
        except (InvalidIdTokenError, KeyError):
            return JSONResponse(
                {"detail": "Unauthorized: Invalid or expired token"}, status_code=401
            )
        except Exception:
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)

        return await call_next(request)
