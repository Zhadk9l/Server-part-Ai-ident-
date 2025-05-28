from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Car
from schemas import CarOut, CarCreate
from crud import get_cars, create_car, delete_car
from typing import List

router = APIRouter(
    tags=["Cars"]
)

@router.get("/get_cars/", response_model=List[CarOut], summary="Отримати всі автомобілі")
def get_cars_endpoint(db: Session = Depends(get_db)):
    return get_cars(db)

@router.get("/get_car/{car_id}", response_model=CarOut, summary="Отримати автомобілі по ID")
def get_car_endpoint(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.car_id == car_id).first()
    if car:
        return car
    return JSONResponse(status_code=404, content={"message": "Car not found"})

@router.post("/create_car/", response_model=CarOut, summary="Створити автомобілі")
def create_car_endpoint(car: CarCreate, db: Session = Depends(get_db)):
    return create_car(db, car.make, car.model, car.year, car.license_plate, car.status)

@router.delete("/delete_car/{car_id}", response_model=CarOut, summary="Видалити автомобілі")
def delete_car_endpoint(car_id: int, db: Session = Depends(get_db)):
    deleted_car = delete_car(db, car_id)
    if deleted_car:
        return deleted_car
    return JSONResponse(status_code=404, content={"message": "Car not found"})
