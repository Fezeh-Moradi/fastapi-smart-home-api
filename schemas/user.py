from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=3)
    phone: str
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    phone: str
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    phone: str