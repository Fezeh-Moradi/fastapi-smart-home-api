from schemas.device import DeviceCreate
from bson import ObjectId
from fastapi import HTTPException, status
from database.mongodb import users_collection, devices_collection

def validate_object_id(owner_id: str) -> ObjectId:
    if not ObjectId.is_valid(owner_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID"
        )
    return ObjectId(owner_id)



    

async def create_device(device: DeviceCreate):
    
    object_owner_id = validate_object_id(device.owner_id)

    owner = await users_collection.find_one(
        {"_id": object_owner_id}
    )
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )
    
    existing_device = await devices_collection.find_one(
        {"serial_number": device.serial_number}
    )
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Serial number already exists"
        )
    
    device_data = device.model_dump()
    device_data["owner_id"] = object_owner_id
    device_data["is_online"] = False

    result = await devices_collection.insert_one(device_data)

    return{
        "message": "Device created successfully",
        "id": str(result.inserted_id)
    }




async def get_devices():
    pipeline = [
        {
            "$lookup": {
                "from": "users",
                "localField": "owner_id",
                "foreignField": "_id",
                "as": "owner"
            }
        },
        {
            "$unwind": "$owner"
        },
        {
            "$project": {
                "_id": 0,

                "id": {
                    "$toString": "$_id"
                },

                "name": 1,
                "device_type": 1,
                "serial_number": 1,
                "status": 1,
                "is_online": 1,

                "owner": {
                    "id": {
                        "$toString": "$owner._id"
                    },
                    "name": "$owner.name",
                    "phone": "$owner.phone"
                }
            }
        }
    ]

    cursor = devices_collection.aggregate(pipeline)

    devices = []

    async for device in cursor:
        devices.append(device)
        print(device)

    return devices

    
