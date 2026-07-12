from fastapi import APIRouter, HTTPException, status, Query
from schemas.user import UserCreate, UserResponse, UserUpdate, UserListResponse
from core.security import hash_password
from database.mongodb import users_collection
from bson import ObjectId

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    users = []

    total = await users_collection.count_documents({})

    cursor = users_collection.find().skip(skip).limit(limit)

    async for user in cursor:
        user["id"] =  str(user.pop("_id"))
        users.append(user)

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": users
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):

    if not ObjectId.is_valid(user_id):
        raise HTTPException(400, "Invalid ID")

    user = await users_collection.find_one(
        {"_id": ObjectId(user_id)}
    )

    if not user:
        raise HTTPException(404, "User not found")

    user["id"] = str(user.pop("_id"))

    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):

    existing_user = await users_collection.find_one(
        {"phone": user.phone}
    )

    if existing_user:
        raise HTTPException(400, "Phone already exists")

    result = await users_collection.insert_one(user.dict())

    return {
        "message": "User created",
        "id": str(result.inserted_id)
    }


@router.put("/{user_id}")
async def update_user(user_id: str, user: UserUpdate):

    if not ObjectId.is_valid(user_id):
        raise HTTPException(400, "Invalid ID")

    update_data = user.model_dump(exclude_unset=True)

    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(404, "User not found")

    return {"message": "User updated successfully"}


@router.delete("/{user_id}")
async def delete_user(user_id: str):

    if not ObjectId.is_valid(user_id):
        raise HTTPException(400, "Invalid ID")

    result = await users_collection.delete_one(
        {"_id": ObjectId(user_id)}
    )

    if result.deleted_count == 0:
        raise HTTPException(404, "User not found")

    return {"message": "User deleted successfully"}