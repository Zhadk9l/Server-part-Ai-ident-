from pydantic import BaseModel
from typing import List
from datetime import datetime

class CarCreate(BaseModel):
    make: str
    model: str
    year: int
    license_plate: str
    status: str

    class Config:
        from_attributes = True

class CarOut(BaseModel):
    car_id: int
    make: str
    model: str
    year: int
    license_plate: str
    status: str

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    phone: str
    email: str
    tg_id: int

    class Config:
        from_attributes = True

class RentalCreate(BaseModel):
    car_id: int
    user_id: int
    rental_start: datetime
    rental_end: datetime
    damage_check: bool
    is_ended: bool
    has_new_damage: bool = False

    class Config:
        from_attributes = True

class RentalOut(BaseModel):
    rental_id: int
    car_id: int
    user_id: int
    rental_start: datetime
    rental_end: datetime
    damage_check: bool
    is_ended: bool
    has_new_damage: bool = False

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    tg_id: int

    class Config:
        from_attributes = True


class AdminCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

    class Config:
        from_attributes = True

class AdminOut(BaseModel):
    admin_id: int
    first_name: str
    last_name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True