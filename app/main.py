# Import necessary modules
# FastAPI for building the API
# Database collections
# Routers for different API endpoints
# JSON response and exception handling
# CORS middleware for handling cross-origin requests
# Logger for logging
# Firebase authentication middleware
# Firebase admin setup
# WebSocket manager for handling active connections

from fastapi import FastAPI, WebSocket
from app.db.collections import db
from app.routes.org_routes import router as org_router
from app.routes.user_routes import router as user_router
from app.routes.team_routes import router as team_router
from app.routes.service_routes import router as service_router
from app.routes.incident_routes import router as incident_router
from app.routes.status_routes import router as status_router
from app.routes.log_routes import router as log_router
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.core.logger import logger
from app.middleware.firebase_auth import FirebaseAuthMiddleware
import app.core.firebase_admin
from app.websocket_manager import active_connections

# Create a FastAPI application instance
app = FastAPI()

# Add Firebase authentication middleware
app.add_middleware(FirebaseAuthMiddleware)

# Include routers for different API endpoints
app.include_router(org_router)  # Organization routes
app.include_router(user_router)  # User routes
app.include_router(team_router)  # Team routes
app.include_router(service_router)  # Service routes
app.include_router(incident_router)  # Incident routes
app.include_router(status_router)  # Status routes
app.include_router(log_router)  # Log routes

# Add CORS middleware if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,  # Allow credentials
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


# Root endpoint to check API status
@app.get("/")
async def root():
    status = await db.command("ping")  # Check database connection
    return {"message": "API is running", "db_status": status}


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)  # Log the exception
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred."},
    )


# WebSocket endpoint for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    active_connections.append(websocket)  # Add to active connections
    try:
        while True:
            data = await websocket.receive_text()  # Receive data from the client
            # Process the received data and send a response
            await websocket.send_text(f"Message text was: {data}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")  # Log WebSocket errors
    finally:
        active_connections.remove(websocket)  # Remove from active connections
        active_connections.remove(websocket)
        await websocket.close()
