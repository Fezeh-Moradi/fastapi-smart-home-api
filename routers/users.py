from fastapi import APIRouter, status, Query
from schemas.user import UserCreate, UserResponse, UserUpdate, UserListResponse
from typing import Literal
from services import user_service

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: str | None = Query(None),
    phone: str | None = Query(None),
    sort: Literal["name", "-name", "phone", "-phone"] = Query("name")
):
    return await user_service.get_users(
        skip=skip,
        limit=limit,
        name=name,
        phone=phone,
        sort=sort,
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    return await user_service.get_user(user_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    return await user_service.create_user(user)

@router.put("/{user_id}")
async def update_user(user_id: str, user: UserUpdate):
    return await user_service.update_user(user_id, user)

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    return await user_service.delete_user(user_id)

    