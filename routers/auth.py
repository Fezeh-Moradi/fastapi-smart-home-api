from fastapi import APIRouter, Depends, HTTPException

from core.deps import get_current_user
from core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from database.mongodb import users_collection
from schemas.user import (
    UserCreate,
    UserLogin,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.get("/me")
async def get_me(
        user_id: str = Depends(get_current_user)
):
    return {
        "user_id": user_id
    }


@router.post("/register")
async def register(user: UserCreate):

    existing_user = await users_collection.find_one(
        {"phone": user.phone}
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    user_dict = user.model_dump()

    user_dict["password"] = hash_password(
        user.password
    )

    result = await users_collection.insert_one(
        user_dict
    )

    return {
        "message": "User registered successfully",
        "id": str(result.inserted_id)
    }


@router.post("/login")
async def login(user: UserLogin):

    db_user = await users_collection.find_one(
        {"phone": user.phone}
    )

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not verify_password(
            user.password,
            db_user["password"]
    ):
        raise HTTPException(
            status_code=400,
            detail="Wrong password"
        )

    token = create_access_token(
        {
            "user_id": str(db_user["_id"])
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }