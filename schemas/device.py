from pydantic import BaseModel
from typing import Literal
from enum import Enum


class DeviceStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"

class DeviceType(str, Enum):
    light = "light"
    sensor = "sensor"
    relay = "relay"
    camera = "camera"


class DeviceOwner(BaseModel):
    id: str
    name: str
    phone: str

class DeviceCreate(BaseModel):
    name: str
    device_type: DeviceType
    serial_number: str
    owner_id: str
    status: DeviceStatus

class DeviceUpdate(BaseModel):
    name: str | None = None
    device_type: DeviceType | None = None
    serial_number: str | None = None
    status: DeviceStatus | None = None
    owner_id: str | None = None

class DeviceResponse(BaseModel):
    id: str
    name: str
    device_type: DeviceType
    serial_number: str
    status: DeviceStatus
    is_online: bool
    owner: DeviceOwner

class DeviceListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[DeviceResponse]



