from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from typing import Literal
from database.mongodb import devices_collection
from schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse, DeviceListResponse, DeviceStatus, DeviceType
from core.deps import get_current_user
from services import device_service

router = APIRouter(
    prefix="/devices",
    tags=["Devices"]
)

@router.post("/")
async def create_device(
    device: DeviceCreate,
    current_user: str = Depends(get_current_user),
):
    return await device_service.create_device(
        device,
        current_user,
    )


@router.get("/", response_model=DeviceListResponse)
async def get_devices(
    current_user: str = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort: Literal["name", "-name"] = Query("name"),
    status: DeviceStatus | None = Query(None),
    device_type: DeviceType | None = Query(None),
    is_online: bool | None = Query(None),
):
    return await device_service.get_devices(
        skip = skip,
        limit = limit,
        sort = sort,
        status = status,
        device_type = device_type,
        current_user=current_user,
        is_online = is_online,
    )



@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    current_user: str = Depends(get_current_user),
):
    return await device_service.get_device(
        device_id,
        current_user,
    )


@router.put("/{device_id}")
async def update_device(
    device_id: str,
    device: DeviceUpdate,
    current_user: str = Depends(get_current_user)
):
    return await device_service.update_device(
        device_id,
        device,
        current_user,
    )


@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    current_user: str = Depends(get_current_user),
):
    return await device_service.delete_device(
        device_id,
        current_user,
    )