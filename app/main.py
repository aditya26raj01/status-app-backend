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

app = FastAPI()
app.add_middleware(FirebaseAuthMiddleware)

app.include_router(org_router)
app.include_router(user_router)
app.include_router(team_router)
app.include_router(service_router)
app.include_router(incident_router)
app.include_router(status_router)
app.include_router(log_router)

# Add CORS middleware if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    status = await db.command("ping")
    return {"message": "API is running", "db_status": status}


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred."},
    )


# # Validation error handler
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc):
#     logger.error(f"Validation error: {exc}", exc_info=True)
#     return JSONResponse(
#         status_code=422,
#         content={"message": "Validation error.", "details": exc.errors()},
#     )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process the received data and send a response
            await websocket.send_text(f"Message text was: {data}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        active_connections.remove(websocket)
        await websocket.close()
