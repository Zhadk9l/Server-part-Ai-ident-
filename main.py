from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from database import Base, engine
import os

# Імпорт всех роутеров
from routers import admin, cars, users, rentals, photos, admins

app = FastAPI(title="Car Damage Detection API")

# Створення усіх таблиц в базе даних
Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Підключення роутеров
app.include_router(admin.router)
app.include_router(cars.router)
app.include_router(users.router)
app.include_router(rentals.router)
app.include_router(photos.router)
app.include_router(admins.router)

# Точка входа
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
