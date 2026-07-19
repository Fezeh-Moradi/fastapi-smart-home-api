from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from typing import Literal
from database.mongodb import devices_collection
from schemas.device import DeviceCreate, DeviceListResponse, DeviceStatus, DeviceType
from core.deps import get_current_user
from services import device_service

router = APIRouter(
    prefix="/devices",
    tags=["Devices"]
)

@router.post("/")
async def create_device(device: DeviceCreate):
    return await device_service.create_device(device)


@router.get("/", response_model=DeviceListResponse)
async def get_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort: Literal["name", "-name"] = Query("name"),

    status: DeviceStatus | None = Query(None),
    device_type: DeviceType | None = Query(None),
    owner_id: str | None = Query(None),
    is_online: bool | None = Query(None),
):
    return await device_service.get_devices(
        skip = skip,
        limit = limit,
        sort = sort,
        status = status,
        device_type = device_type,
        owner_id = owner_id,
         is_online = is_online,
    )