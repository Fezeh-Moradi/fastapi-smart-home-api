from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from database.mongodb import devices_collection
from schemas.device import DeviceCreate
from core.deps import get_current_user

router = APIRouter(
    prefix="/devices",
    tags=["Devices"]
)


@router.post("/")
async def create_device(
    device: DeviceCreate,
    user_id: str = Depends(get_current_user)
):

    device_dict = device.model_dump()

    device_dict["owner_id"] = user_id

    result = await devices_collection.insert_one(
        device_dict
    )

    return {
        "message": "Device created successfully",
        "id": str(result.inserted_id)
    }


@router.get("/")
async def get_my_devices(
    user_id: str = Depends(get_current_user)
):

    devices = []

    cursor = devices_collection.find(
        {"owner_id": user_id}
    )

    async for device in cursor:
        device["_id"] = str(device["_id"])
        devices.append(device)

    return devices


@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    user_id: str = Depends(get_current_user)
):

    if not ObjectId.is_valid(device_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid device id"
        )

    result = await devices_collection.delete_one(
        {
            "_id": ObjectId(device_id),
            "owner_id": user_id
        }
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    return {
        "message": "Device deleted successfully"
    }