from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from crud import get_users, create_user, delete_user
from schemas import UserCreate, UserOut
from typing import List

router = APIRouter(
    tags=["Users"]
)

@router.get("/get_users/", response_model=List[UserOut], summary="Отримати усіх користувачів")
def get_users_endpoint(db: Session = Depends(get_db)):
    return get_users(db)

@router.post("/create_user/", response_model=UserOut, summary="Створити користувача")
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, user.first_name, user.last_name, user.phone, user.email, user.tg_id)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.delete("/delete_user/{user_id}", response_model=UserOut, summary="Видалити користувача")
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    deleted_user = delete_user(db, user_id)
    if deleted_user:
        return deleted_user
    return JSONResponse(status_code=404, content={"message": "User not found"})
