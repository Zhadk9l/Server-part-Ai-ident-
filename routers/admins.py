from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Admin
from crud import get_admins, create_admin, delete_admin, get_admin_by_email
from schemas import AdminCreate, AdminOut
from typing import List

router = APIRouter(
    tags=["Admins"]
)

@router.post("/create_admin/", response_model=AdminOut)
def create_admin_endpoint(admin: AdminCreate, db: Session = Depends(get_db)):
    existing_admin = get_admin_by_email(db, admin.email)
    if existing_admin:
        return JSONResponse(status_code=400, content="Адміністратор з таким email вже існує.")
    return create_admin(db, admin.first_name, admin.last_name, admin.email, admin.password)

@router.get("/admins/", response_model=List[AdminOut])
def get_admins_endpoint(db: Session = Depends(get_db)):
    return get_admins(db)

@router.delete("/delete_admin/{admin_id}", response_model=AdminOut)
def delete_admin_endpoint(admin_id: int, db: Session = Depends(get_db)):
    deleted_admin = delete_admin(db, admin_id)
    if not deleted_admin:
        return JSONResponse(status_code=404, content="Адміністратор не знайдений.")
    return deleted_admin
