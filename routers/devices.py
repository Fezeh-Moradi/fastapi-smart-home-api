from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from database.mongodb import devices_collection
from schemas.device import DeviceCreate
from core.deps import get_current_user
from services import device_service

router = APIRouter(
    prefix="/devices",
    tags=["Devices"]
)

@router.post("/")
async def create_device(device: DeviceCreate):
    return await device_service.create_device(device)


@router.get("/")
async def get_devices():
    return await device_service.get_devices()