from database.mongodb import users_collection
from core.security import hash_password
from fastapi import HTTPException, status
from bson import ObjectId
from schemas.user import UserCreate, UserUpdate


def serialize_user(user: dict) -> dict:
    user["id"] = str(user.pop("_id"))
    return user


def validate_object_id(user_id: str) -> ObjectId:
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID"
        )

    return ObjectId(user_id)

async def get_users(
    skip: int,
    limit: int,
    name: str | None,
    phone: str | None,
    sort: str,
):
    users = []
    filters = {}

    if name:
        filters["name"] = {
            "$regex": name,
            "$options": "i"
        }

    if phone:
        filters["phone"] = phone

    total = await users_collection.count_documents(filters)

    if sort.startswith("-"):
        sort_field = sort[1:]
        sort_order = -1
    else:
        sort_field = sort
        sort_order = 1

    cursor = (
        users_collection
        .find(filters)
        .sort(sort_field, sort_order)
        .skip(skip)
        .limit(limit)
    )

    async for user in cursor:
        
        users.append(serialize_user(user))

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": users
    }


async def get_user(user_id: str):

    object_id = validate_object_id(user_id)

    user = await users_collection.find_one(
        {"_id": object_id}
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return serialize_user(user)


async def create_user(user: UserCreate):
    existing_user = await users_collection.find_one(
        {"phone": user.phone}
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone already exists"
        )

    user_data = user.model_dump()

    user_data["password"] = hash_password(user.password)

    result = await users_collection.insert_one(user_data)

    return {
        "message": "User created",
        "id": str(result.inserted_id)
    }


async def update_user(user_id: str, user: UserUpdate):

    object_id = validate_object_id(user_id)

    update_data = user.model_dump(exclude_unset=True)


    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])


    result = await users_collection.update_one(
        {"_id": object_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"message": "User updated successfully"}


async def delete_user(user_id: str):

    object_id = validate_object_id(user_id)

    result = await users_collection.delete_one(
        {"_id": object_id}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"message": "User deleted successfully"}
