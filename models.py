from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float, LargeBinary, JSON
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.dialects.mssql import NVARCHAR


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20), unique=True)
    email = Column(String(100), unique=True)
    tg_id = Column(Integer, unique=True, nullable=True)  # Добавляем поле tg_id
    created_at = Column(DateTime)

    rentals = relationship("Rental", back_populates="user")



class Car(Base):
    __tablename__ = "cars"

    car_id = Column(Integer, primary_key=True, index=True)
    make = Column(String(50))
    model = Column(String(50))
    year = Column(Integer)
    license_plate = Column(String(20), unique=True)
    status = Column(String(50))

    rentals = relationship("Rental", back_populates="car")


class Rental(Base):
    __tablename__ = "rentals"

    rental_id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.car_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    rental_start = Column(DateTime)
    rental_end = Column(DateTime)
    has_new_damage = Column(Boolean, default=False)
    damage_check = Column(Boolean, default=False)
    is_ended = Column(Boolean, default=False)

    car = relationship("Car", back_populates="rentals")
    user = relationship("User", back_populates="rentals")
    rental_photos = relationship("RentalPhoto", back_populates="rental", cascade="all, delete-orphan")


class RentalPhoto(Base):
    __tablename__ = "rental_photos"

    photo_id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, ForeignKey("rentals.rental_id"))
    photo_path = Column(String(255))
    photo_type = Column(String(50))
    created_at = Column(DateTime)

    rental = relationship("Rental", back_populates="rental_photos")  # Связь с арендами
    damages = relationship("Damage", back_populates="rental_photo", cascade="all, delete-orphan")


class Damage(Base):
    __tablename__ = "damages"

    damage_id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(Integer, ForeignKey("rental_photos.photo_id"))
    damage_type = Column(String(50))
    confidence = Column(Float)
    box = Column(NVARCHAR(255))  # Указание длины для NVARCHAR в MySQL
    created_at = Column(DateTime)

    rental_photo = relationship("RentalPhoto", back_populates="damages")


class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(100), unique=True)
    password = Column(String(255))  # Пароль в зашифрованном виде
    created_at = Column(DateTime)
