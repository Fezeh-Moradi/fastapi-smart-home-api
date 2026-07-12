from pydantic import BaseModel, Field, field_validator


class UserBase(BaseModel):
    name: str = Field(min_length=3)
    phone: str

    @field_validator("phone")
    @classmethod

    def validate_phone(cls, value):
        if not value.startswith("09"):
            raise ValueError("Phone number must start with 09")
        
        if len(value) !=11:
            raise ValueError("Phone number must be 11 digits")
        
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits")
        
        return value


class UserCreate(UserBase):
    password: str = Field(min_length=6)


    


class UserLogin(BaseModel):
    phone: str
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    phone: str


class UserListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[UserResponse]
    


class UserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    password: str | None = None
