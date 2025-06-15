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


router = APIRouter(prefix="/service", tags=["Services"])


@router.post("/create-service", response_model=Service)
async def create_service(
    service_data: ServiceCreate, user: User = Depends(get_current_user)
):
    service = Service(
        name=service_data.name,
        description=service_data.description,
        status=service_data.status,
        org_id=PyObjectId(service_data.org_id),
        created_by=user.id,  # type: ignore
        # because if code reaches here, user is not None
    )
    # Save the service and get the inserted ID
    result = await service.save()
    service.id = result.id  # Ensure the ID is set

    if service.id is None:
        raise HTTPException(
            status_code=500, detail="Service ID is not set after saving."
        )

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

    await broadcast_message({"type": "service", "data": result.model_dump_json()})
    return result


@router.post("/update-service", response_model=Service)
async def update_service(
    service_data: ServiceUpdate, user: User = Depends(get_current_user)
):
    service = await Service.find_by_id(service_data.service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    if not user.current_org:
        raise HTTPException(
            status_code=403, detail="You are not authorized to update this service"
        )
    if str(service.org_id) != str(user.current_org.org_id):
        raise HTTPException(
            status_code=403, detail="You are not authorized to update this service"
        )
    service.name = service_data.name
    service.description = service_data.description
    service.status = service_data.status
    service = await service.update(
        {
            "name": service.name,
            "description": service.description,
            "status": service.status,
        }
    )

    if service.id is None:
        raise HTTPException(
            status_code=500, detail="Service ID is not set after update."
        )

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

    await broadcast_message({"type": "service", "data": service.model_dump_json()})
    return service


@router.get("/get-all-services", response_model=List[Service])
async def list_services(org_id: str, user: User = Depends(get_current_user)):
    services = await Service.find_all(
        {
            "org_id": PyObjectId(org_id),
        }
    )
    return services


@router.delete("/delete-service", response_model=Service)
async def delete_service(service_id: str, user: User = Depends(get_current_user)):
    service = await Service.find_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    if not user.current_org:
        raise HTTPException(
            status_code=403, detail="You are not authorized to delete this service"
        )
    if str(service.org_id) != str(user.current_org.org_id):
        raise HTTPException(
            status_code=403, detail="You are not authorized to delete this service"
        )
    await service.delete()

    if service.id is None:
        raise HTTPException(
            status_code=500, detail="Service ID is not set after deletion."
        )

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

    await broadcast_message(
        {"type": "service", "data": service.model_dump_json(), "action": "delete"}
    )
    return service


@router.get("/{service_id}", response_model=Service)
async def fetch_service(service_id: str):
    service = await Service.find_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
