from sqlalchemy.orm import Session
from models import Car, Rental, User, RentalPhoto, Admin
from datetime import datetime


# Функція для отримання усіх автомобилей
def get_cars(db: Session):
    return db.query(Car).all()

# Функція для отримання автомобиля по его ID
def get_car(db: Session, car_id: int):
    return db.query(Car).filter(Car.car_id == car_id).first()

# Функція для створення нового автомобіля
def create_car(db: Session, make: str, model: str, year: int, license_plate: str, status: str):
    db_car = Car(make=make, model=model, year=year, license_plate=license_plate, status=status)
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

# Функция для удаления автомобиля
def delete_car(db: Session, car_id: int):
    car_to_delete = db.query(Car).filter(Car.car_id == car_id).first()
    if car_to_delete:
        db.delete(car_to_delete)
        db.commit()
        return car_to_delete
    return None

# Функция для получения всех аренда
def get_rentals(db: Session):
    return db.query(Rental).all()
# Create a new rental
def create_rental(db: Session, car_id: int, user_id: int, rental_start: str, rental_end: str, damage_check: bool, is_ended: bool, has_new_damage: bool = False):
    db_rental = Rental(
        car_id=car_id,
        user_id=user_id,
        rental_start=rental_start,
        rental_end=rental_end,
        damage_check=damage_check,
        is_ended=is_ended,
        has_new_damage=has_new_damage,
    )
    db.add(db_rental)
    db.commit()
    db.refresh(db_rental)
    return db_rental

# Видалити оренду
def delete_rental(db: Session, rental_id: int):
    rental_to_delete = db.query(Rental).filter(Rental.rental_id == rental_id).first()
    if rental_to_delete:
        db.delete(rental_to_delete)
        db.commit()
        return rental_to_delete
    return None

# Функция для получения всех пользователей
def get_users(db: Session):
    return db.query(User).all()
# Create a new user
def create_user(db: Session, first_name: str, last_name: str, phone: str, email: str, tg_id: int):
    db_user = User(first_name=first_name, last_name=last_name, phone=phone, email=email, tg_id=tg_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Видалити юзера
def delete_user(db: Session, user_id: int):
    user_to_delete = db.query(User).filter(User.user_id == user_id).first()
    if user_to_delete:
        db.delete(user_to_delete)
        db.commit()
        return user_to_delete
    return None

# Функция для отримання изображення по ID
def get_image(db: Session, photo_id: int):
    photo = db.query(RentalPhoto).filter(RentalPhoto.photo_id == photo_id).first()
    if photo:
        return photo.photo_data  # Возвращаем данные изображения в виде байтов
    return None

# Функція для створення нового адміністратора
def create_admin(db: Session, first_name: str, last_name: str, email: str, password: str):
    created_at = datetime.now()
    db_admin = Admin(first_name=first_name, last_name=last_name, email=email, password=password, created_at=created_at)
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

# Функція для отримання всіх адміністраторів
def get_admins(db: Session):
    return db.query(Admin).all()

# Функція для отримання адміністратора за email
def get_admin_by_email(db: Session, email: str):
    return db.query(Admin).filter(Admin.email == email).first()

# Функція для видалення адміністратора за id
def delete_admin(db: Session, admin_id: int):
    admin_to_delete = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if admin_to_delete:
        db.delete(admin_to_delete)
        db.commit()
        return admin_to_delete
    return None