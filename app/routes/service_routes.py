# Import necessary modules and dependencies
# FastAPI components for routing and exceptions
# Custom models and schemas for services and users
# Authentication dependency
# Typing for type hints
# Websocket manager for broadcasting messages
from fastapi import APIRouter, HTTPException
from app.models.base import PyObjectId
from app.models.service_model import Service
from app.schemas.service_schema import ServiceCreate, ServiceUpdate
from app.models.user_model import User
from app.dependencies.auth import get_current_user
from fastapi import Depends
from typing import List
from app.models.log_model import LogEntry, EntityType, ChangeType
from app.websocket_manager import broadcast_message


# Create a router for service-related endpoints with a prefix and tags
router = APIRouter(prefix="/service", tags=["Services"])


# Endpoint to create a new service
# Accepts service data and the current user as input
# Returns the created service
@router.post("/create-service", response_model=Service)
async def create_service(
    service_data: ServiceCreate, user: User = Depends(get_current_user)
):
    # Create a new service object from the provided data
    # Set the name, description, status, and organization ID
    # Set the creator information
    service = Service(
        name=service_data.name,
        description=service_data.description,
        status=service_data.status,
        org_id=PyObjectId(service_data.org_id),
        created_by=user.id,  # type: ignore
        # because if code reaches here, user is not None
        created_by_username=user.full_name,
    )
    # Save the service and get the inserted ID
    result = await service.save()
    service.id = result.id  # Ensure the ID is set

    # Check if the service ID is set after saving
    # Raise an HTTPException if not
    if service.id is None:
        raise HTTPException(
            status_code=500, detail="Service ID is not set after saving."
        )

    # Check if the user ID is available
    # Raise an HTTPException if not
    if user.id is None:
        raise HTTPException(status_code=500, detail="User ID is not available.")

    # Log the creation of the service
    log_entry = LogEntry(
        entity_id=service.id,
        entity_type=EntityType.SERVICE,
        change_type=ChangeType.CREATE,
        changes={
            "name": service.name,
            "description": service.description,
            "status": service.status,
        },
        org_id=service.org_id,
        created_by=user.id,
    )
    await log_entry.save()

    # Broadcast the creation of the service to connected clients
    await broadcast_message({"type": "service", "data": result.model_dump_json()})
    return result


# Endpoint to update an existing service
# Accepts updated service data and the current user as input
# Returns the updated service
@router.post("/update-service", response_model=Service)
async def update_service(
    service_data: ServiceUpdate, user: User = Depends(get_current_user)
):
    # Find the service by its ID
    # Raise an HTTPException if not found
    service = await Service.find_by_id(service_data.service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    # Check if the user is authorized to update the service
    # Raise an HTTPException if not
    if not user.current_org:
        raise HTTPException(
            status_code=403, detail="You are not authorized to update this service"
        )
    if str(service.org_id) != str(user.current_org.org_id):
        raise HTTPException(
            status_code=403, detail="You are not authorized to update this service"
        )
    # Update the service's name, description, and status
    service.name = service_data.name
    service.description = service_data.description
    service.status = service_data.status
    # Update the service in the database
    service = await service.update(
        {
            "name": service.name,
            "description": service.description,
            "status": service.status,
        }
    )

    # Check if the service ID is set after updating
    # Raise an HTTPException if not
    if service.id is None:
        raise HTTPException(
            status_code=500, detail="Service ID is not set after update."
        )

    # Check if the user ID is available
    # Raise an HTTPException if not
    if user.id is None:
        raise HTTPException(status_code=500, detail="User ID is not available.")

    # Log the update of the service
    log_entry = LogEntry(
        entity_id=service.id,
        entity_type=EntityType.SERVICE,
        change_type=ChangeType.UPDATE,
        changes={
            "name": service.name,
            "description": service.description,
            "status": service.status,
        },
        org_id=service.org_id,
        created_by=user.id,
    )
    await log_entry.save()

    # Broadcast the update of the service to connected clients
    await broadcast_message({"type": "service", "data": service.model_dump_json()})
    return service


# Endpoint to list all services for a given organization
# Accepts organization ID and the current user as input
# Returns a list of services
@router.get("/get-all-services", response_model=List[Service])
async def list_services(org_id: str, user: User = Depends(get_current_user)):
    # Find all services for the given organization ID
    services = await Service.find_all(
        {
            "org_id": PyObjectId(org_id),
        }
    )
    # Return the list of services
    return services


# Endpoint to delete a service
# Accepts service ID and the current user as input
# Returns the deleted service
@router.delete("/delete-service", response_model=Service)
async def delete_service(service_id: str, user: User = Depends(get_current_user)):
    # Find the service by its ID
    # Raise an HTTPException if not found
    service = await Service.find_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    # Check if the user is authorized to delete the service
    # Raise an HTTPException if not
    if not user.current_org:
        raise HTTPException(
            status_code=403, detail="You are not authorized to delete this service"
        )
    if str(service.org_id) != str(user.current_org.org_id):
        raise HTTPException(
            status_code=403, detail="You are not authorized to delete this service"
        )
    # Delete the service from the database
    await service.delete()

    # Check if the service ID is set after deletion
    # Raise an HTTPException if not
    if service.id is None:
        raise HTTPException(
            status_code=500, detail="Service ID is not set after deletion."
        )

    # Check if the user ID is available
    # Raise an HTTPException if not
    if user.id is None:
        raise HTTPException(status_code=500, detail="User ID is not available.")

    # Log the deletion of the service
    log_entry = LogEntry(
        entity_id=service.id,
        entity_type=EntityType.SERVICE,
        change_type=ChangeType.DELETE,
        changes={},
        org_id=service.org_id,
        created_by=user.id,
    )
    await log_entry.save()

    # Broadcast the deletion of the service to connected clients
    await broadcast_message(
        {"type": "service", "data": service.model_dump_json(), "action": "delete"}
    )
    return service


# Endpoint to fetch a specific service by its ID
# Accepts service ID as input
# Returns the service if found
@router.get("/{service_id}", response_model=Service)
async def fetch_service(service_id: str):
    # Find the service by its ID
    # Raise an HTTPException if not found
    service = await Service.find_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    # Return the service
    return service
