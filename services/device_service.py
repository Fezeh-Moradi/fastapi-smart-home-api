from schemas.device import DeviceCreate, DeviceUpdate, DeviceType, DeviceStatus
from bson import ObjectId
from fastapi import HTTPException, status
from database.mongodb import users_collection, devices_collection

def validate_object_id(id: str) -> ObjectId:
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID"
        )
    return ObjectId(id)

async def validate_current_user(user_id: str) -> ObjectId:
    object_user_id  = validate_object_id(user_id)

    user = await users_collection.find_one(
        {"_id": object_user_id }
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return object_user_id 

async def validate_serial_number(
        serial_number: str,
        exclude_id: ObjectId | None = None,
):
    query = {
        "serial_number": serial_number
    }

    if exclude_id:
        query["_id"] = {
            "$ne": exclude_id
        }

    existing_device = await devices_collection.find_one(query)

    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Serial number already exists"
        )


async def validate_device(device_id: str):
    object_id = validate_object_id(device_id)

    device = await devices_collection.find_one(
        {"_id": object_id}
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    return object_id

def get_device_pipeline():
    return [
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
                "id": {"$toString": "$_id"},
                "name": 1,
                "device_type": 1,
                "serial_number": 1,
                "status": 1,
                "is_online": 1,
                "owner": {
                    "id": {"$toString": "$owner._id"},
                    "name": "$owner.name",
                    "phone": "$owner.phone"
                }
            }
        }
    ]


    

async def create_device(
        device: DeviceCreate,
        current_user: str,
):
    
    object_user_id  = await validate_current_user(current_user)
    
    await validate_serial_number(device.serial_number)
    
    device_data = device.model_dump()
    device_data["owner_id"] = object_user_id 
    device_data["is_online"] = False

    result = await devices_collection.insert_one(device_data)

    return{
        "message": "Device created successfully",
        "id": str(result.inserted_id)
    }


async def get_devices(
    skip: int,
    limit: int,
    sort: str,
    status: DeviceStatus | None,
    device_type: DeviceType | None,
    owner_id: str | None,
    is_online: bool | None,
):
    
    if sort.startswith("-"):
        sort_field = sort[1:]
        sort_order = -1

    else:
        sort_field = sort
        sort_order = 1

    filters = {}

    if status:
        filters["status"] = status

    if device_type:
        filters["device_type"] = device_type

    if is_online is not None:
        filters["is_online"] = is_online

    if owner_id:
        filters["owner_id"] = validate_object_id(owner_id)

    pipeline = [
        {
            "$match": filters
        }

    ]

    pipeline.extend(get_device_pipeline())

    pipeline.extend([

        {
            "$sort": {
                sort_field: sort_order
            }
        },
        {
            "$skip": skip
        },
        {
            "$limit": limit
        }

    ])

    total = await devices_collection.count_documents(filters)
    cursor = devices_collection.aggregate(pipeline)

    devices = []

    async for device in cursor:
        devices.append(device)

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": devices
    }



async def get_device(device_id: str):
    object_id = validate_object_id(device_id)

    pipeline = [
        {
            "$match":{
                "_id": object_id
            }
        }
    ]

    pipeline.extend(get_device_pipeline())

    cursor = devices_collection.aggregate(pipeline)

    device = None

    async for item in cursor:
        device = item
        break

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    return device



async def update_device(device_id: str, device: DeviceUpdate):
    
    object_id = await validate_device(device_id)
    
    update_data = device.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    

    if "serial_number" in update_data:
        await validate_serial_number(
            update_data["serial_number"],
            exclude_id=object_id,
        )
    
    await devices_collection.update_one(
        {"_id": object_id},
        {"$set": update_data}
    )

    return{
        "message": "Device updated successfully"
    }


async def delete_device(device_id: str):
    object_id = await validate_device(device_id)

    await devices_collection.delete_one(
        {"_id": object_id}
    )

    return {
        "message": "Device deleted successfully"
    }

