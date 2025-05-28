from fastapi import APIRouter, Depends, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Rental, Car, User
from crud import get_rentals, create_rental, delete_rental
from schemas import RentalCreate, RentalOut
from typing import List

router = APIRouter(
    tags=["Rentals"]
)

@router.get("/get_rentals/", response_model=List[RentalOut], summary="Отримати усі аренди")
def get_rentals_endpoint(db: Session = Depends(get_db)):
    return get_rentals(db)

@router.get("/get_rentals_by_tg_id/{tg_id}", response_model=List[RentalOut], summary="Оренди по Telegram ID")
def get_rentals_by_tg_id(tg_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.tg_id == tg_id).first()
    if not user:
        return JSONResponse(status_code=404, content={"message": "User not found"})
    rentals = db.query(Rental).filter(Rental.user_id == user.user_id).all()
    return rentals

@router.post("/create_rental/", response_model=RentalOut, summary="Створити оренду")
def create_rental_endpoint(rental: RentalCreate, db: Session = Depends(get_db)):
    try:
        db_rental = create_rental(db, rental.car_id, rental.user_id, rental.rental_start, rental.rental_end, rental.damage_check, rental.is_ended)
        car = db.query(Car).filter(Car.car_id == rental.car_id).first()
        if car:
            car.status = "in_rent"
            db.commit()
        return db_rental
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.delete("/delete_rental/{rental_id}", response_model=RentalOut, summary="Видалит аренду")
def delete_rental_endpoint(rental_id: int, db: Session = Depends(get_db)):
    deleted_rental = delete_rental(db, rental_id)
    if deleted_rental:
        return deleted_rental
    return JSONResponse(status_code=404, content={"message": "Rental not found"})

@router.patch("/update_rental_damage_check/{rental_id}")
def update_damage_check(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(Rental).filter(Rental.rental_id == rental_id).first()
    if not rental:
        return JSONResponse(status_code=404, content={"message": "Rental not found"})
    rental.damage_check = True
    db.commit()
    return {"message": "Rental updated"}

@router.patch("/update_rental_end/{rental_id}")
def update_rental_end(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(Rental).filter(Rental.rental_id == rental_id).first()
    if not rental:
        return JSONResponse(status_code=404, content={"message": "Rental not found"})
    rental.is_ended = True
    car = db.query(Car).filter(Car.car_id == rental.car_id).first()
    if car:
        car.status = "available"
    db.commit()
    return {"message": "Rental ended"}
@router.patch("/flag_rental_damage/{rental_id}")
def flag_rental_damage(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(Rental).filter(Rental.rental_id == rental_id).first()
    if not rental:
        return JSONResponse(status_code=404, content={"message": "Rental not found"})
    rental.has_new_damage = True
    db.commit()
    return {"message": "Rental flagged as damaged"}