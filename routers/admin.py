import csv
from io import StringIO, BytesIO
from datetime import datetime
from typing import Dict

from fastapi import  APIRouter, Request, Depends, Cookie, HTTPException, Query, Form, Body
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from database import get_db
from models import Car, User, Rental, Admin, RentalPhoto, Damage




templates = Jinja2Templates(directory="templates")
router = APIRouter(
    prefix="/admin",
    tags=["Admin Panel"]
)

# Логін
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_post(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == email).first()
    if admin and admin.password == password:
        response = RedirectResponse(url="/admin/panel", status_code=302)
        response.set_cookie(key="admin", value="true")
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Невірний email або пароль"})

# Панель адміністратора
@router.get("/panel", response_class=HTMLResponse)
def admin_panel(request: Request, admin: str = Cookie(default=None), db: Session = Depends(get_db)):
    if not admin:
        return RedirectResponse(url="/admin/login")
    users = db.query(User).all()
    cars = db.query(Car).all()
    rentals = db.query(Rental).all()
    return templates.TemplateResponse("panel.html", {"request": request, "users": users, "cars": cars, "rentals": rentals})

# Вихід
@router.get("/logout")
def admin_logout():
    response = RedirectResponse(url="/admin/login")
    response.delete_cookie(key="admin")
    return response

@router.get("/cars", response_class=HTMLResponse)
def admin_cars(request: Request, admin: str = Cookie(default=None), db: Session = Depends(get_db)):
    if not admin:
        return RedirectResponse(url="/admin/login")
    cars = db.query(Car).all()
    return templates.TemplateResponse("cars.html", {"request": request, "cars": cars})

@router.get("/add_car", response_class=HTMLResponse)
def add_car_form(request: Request, admin: str = Cookie(default=None)):
    if not admin:
        return RedirectResponse(url="/admin/login")
    return templates.TemplateResponse("add_car.html", {"request": request})

@router.post("/add_car", response_class=HTMLResponse)
def add_car(request: Request, make: str = Form(...), model: str = Form(...), year: int = Form(...), license_plate: str = Form(...), db: Session = Depends(get_db), admin: str = Cookie(default=None)):
    if not admin:
        return RedirectResponse(url="/admin/login")

    try:
        # Перевірка наявності автомобіля з таким же номерним знаком
        existing_car = db.query(Car).filter(Car.license_plate == license_plate).first()
        if existing_car:
            raise Exception(f"Автомобіль з таким номерним знаком ({license_plate}) вже існує.")

        # Додавання нового автомобіля
        new_car = Car(make=make, model=model, year=year, license_plate=license_plate, status="available")
        db.add(new_car)
        db.commit()

        # Перенаправлення на сторінку автомобілів після успішного додавання
        return templates.TemplateResponse("add_car.html", {"request": request, "success": "Автомобіль успішно додано!"})

    except Exception as e:
        # Виведення повідомлення про помилку
        db.rollback()
        return templates.TemplateResponse("add_car.html", {"request": request, "error": str(e)})

@router.patch("/update_car/{car_id}")
def update_car(
    car_id: int,
    data: Dict = Body(...),
    db: Session = Depends(get_db),
    admin: str = Cookie(default=None)
):
    if not admin:
        raise HTTPException(status_code=401, detail="Не авторизовано")

    car = db.query(Car).filter(Car.car_id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Автомобіль не знайдено")

    # Оновлення даних
    car.make = data["make"]
    car.model = data["model"]
    car.year = data["year"]
    car.license_plate = data["license_plate"]
    car.status = data["status"]

    db.commit()
    return {"message": "Автомобіль успішно оновлено"}
# Видалити машину
@router.get("/delete_car/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db)):
    # Перевірка, чи є активні оренди для цього автомобіля
    car = db.query(Car).filter(Car.car_id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Автомобіль не знайдений")

    # Перевіряємо, чи є активні оренди для цього автомобіля
    active_rentals = db.query(Rental).filter(Rental.car_id == car_id, Rental.is_ended == False).first()
    if active_rentals:
        raise HTTPException(status_code=400, detail="Не можна видалити автомобіль, якщо він в оренді")

    # Видалення автомобіля, якщо оренди немає
    db.delete(car)
    db.commit()
    return RedirectResponse(url="/admin/cars")


# Сторінка користувачів
@router.get("/users", response_class=HTMLResponse)
def admin_users(request: Request, admin: str = Cookie(default=None), db: Session = Depends(get_db)):
    if not admin:
        return RedirectResponse(url="/admin/login")
    users = db.query(User).all()
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

# Додати користувача
@router.get("/add_user", response_class=HTMLResponse)
def add_user_form(request: Request, admin: str = Cookie(default=None)):
    if not admin:
        return RedirectResponse(url="/admin/login")
    return templates.TemplateResponse("add_user.html", {"request": request})
@router.patch("/update_user/{user_id}")
def update_user(
    user_id: int,
    data: Dict = Body(...),
    db: Session = Depends(get_db),
    admin: str = Cookie(default=None)
):
    if not admin:
        raise HTTPException(status_code=401, detail="Не авторизовано")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувач не знайдений")

    # Оновлення даних користувача
    user.first_name = data["first_name"]
    user.last_name = data["last_name"]
    user.email = data["email"]
    user.phone = data["phone"]
    user.tg_id = data["tg_id"]

    db.commit()
    return {"message": "Користувач успішно оновлений"}


@router.post("/add_user", response_class=HTMLResponse)
def add_user(request: Request, first_name: str = Form(...), last_name: str = Form(...), phone: str = Form(...),
             email: str = Form(...), tg_id: int = Form(None), db: Session = Depends(get_db),
             admin: str = Cookie(default=None)):
    if not admin:
        return RedirectResponse(url="/admin/login")

    try:
        # Перевірка наявності користувача з таким самим email або телефонним номером
        existing_user = db.query(User).filter((User.phone == phone) | (User.email == email)).first()
        if existing_user:
            raise Exception("Користувач з таким email або телефоном вже існує.")

        # Перевірка наявності користувача з таким Telegram ID
        existing_tg_user = db.query(User).filter(User.tg_id == tg_id).first() if tg_id else None
        if existing_tg_user:
            raise Exception("Користувач з таким Telegram ID вже існує.")

        # Додавання нового користувача
        new_user = User(first_name=first_name, last_name=last_name, phone=phone, email=email, tg_id=tg_id,
                        created_at=datetime.now())
        db.add(new_user)
        db.commit()

        # Перенаправлення на сторінку користувачів після успішного додавання
        return templates.TemplateResponse("add_user.html",
                                          {"request": request, "success": "Користувача успішно додано!"})

    except Exception as e:
        db.rollback()
        return templates.TemplateResponse("add_user.html", {"request": request, "error": str(e)})


# Видалити користувача
@router.get("/delete_user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Користувач не знайдений")

    # Перевірка, чи є активні оренди
    active_rentals = db.query(Rental).filter(Rental.user_id == user_id, Rental.is_ended == False).first()
    if active_rentals:
        raise HTTPException(status_code=400, detail="Не можна видалити користувача, якщо він в оренді")

    db.delete(user)
    db.commit()
    return RedirectResponse(url="/admin/users")


# Сторінка оренд
@router.get("/rentals", response_class=HTMLResponse)
def admin_rentals(request: Request, admin: str = Cookie(default=None), db: Session = Depends(get_db)):
    if not admin:
        return RedirectResponse(url="/admin/login")
    rentals = db.query(Rental).all()
    rentals_data = []
    for rental in rentals:
        user = db.query(User).filter(User.user_id == rental.user_id).first()
        car = db.query(Car).filter(Car.car_id == rental.car_id).first()
        rentals_data.append({
            "rental_id": rental.rental_id,
            "user": user,
            "car": car,
            "rental_start": rental.rental_start,
            "rental_end": rental.rental_end,
            "is_ended": rental.is_ended,
            "has_new_damage": rental.has_new_damage
        })
    return templates.TemplateResponse("rentals.html", {"request": request, "rentals": rentals_data})

# Форма додавання оренди
@router.get("/add_rental", response_class=HTMLResponse)
def add_rental_form(request: Request, admin: str = Cookie(default=None), db: Session = Depends(get_db)):
    if not admin:
        return RedirectResponse(url="/admin/login")
    users = db.query(User).all()
    cars = db.query(Car).filter(Car.status == "available").all()
    return templates.TemplateResponse("add_rental.html", {"request": request, "users": users, "cars": cars})

@router.post("/add_rental", response_class=HTMLResponse)
def add_rental(request: Request, user_id: int = Form(...), car_id: int = Form(...), rental_start: str = Form(...), rental_end: str = Form(...), db: Session = Depends(get_db), admin: str = Cookie(default=None)):
    if not admin:
        return RedirectResponse(url="/admin/login")

    # Створення нової оренди
    new_rental = Rental(user_id=user_id, car_id=car_id, rental_start=rental_start, rental_end=rental_end, damage_check=False, is_ended=False)
    db.add(new_rental)

    # Оновлення статусу автомобіля на "в оренді"
    car = db.query(Car).filter(Car.car_id == car_id).first()
    if car:
        car.status = "in_rent"

    db.commit()

    # Повідомлення про успіх
    return templates.TemplateResponse("add_rental.html", {"request": request, "success": "Оренду успішно створено!"})


# Деталі оренди
@router.get("/rental_details/{rental_id}", response_class=JSONResponse)
def get_rental_details(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(Rental).filter(Rental.rental_id == rental_id).first()
    if not rental:
        return JSONResponse(status_code=404, content={"message": "Оренда не знайдена"})

    user = db.query(User).filter(User.user_id == rental.user_id).first()
    car = db.query(Car).filter(Car.car_id == rental.car_id).first()

    # Отримуємо фотографії до оренди (по типу 'before_')
    photos_before = db.query(RentalPhoto).filter(RentalPhoto.rental_id == rental_id,
                                                 RentalPhoto.photo_type.like('before%')).all()
    photos_after = db.query(RentalPhoto).filter(RentalPhoto.rental_id == rental_id,
                                                RentalPhoto.photo_type.like('after%')).all()
    has_after_photos = len(photos_after) > 0
    # Отримуємо пошкодження
    damages_before = db.query(Damage).join(RentalPhoto).filter(RentalPhoto.rental_id == rental_id,
                                                               RentalPhoto.photo_type.like('before%')).all()
    damages_after = db.query(Damage).join(RentalPhoto).filter(RentalPhoto.rental_id == rental_id,
                                                              RentalPhoto.photo_type.like('after%')).all()

    photos_before_paths = [photo.photo_path for photo in photos_before]
    photos_after_paths = [photo.photo_path for photo in photos_after]

    damages_before_list = [{"damage_type": damage.damage_type, "confidence": damage.confidence} for damage in
                           damages_before]
    damages_after_list = [{"damage_type": damage.damage_type, "confidence": damage.confidence} for damage in
                          damages_after]

    return {
        "user": user,
        "car": car,
        "rental_start": rental.rental_start,
        "rental_end": rental.rental_end,
        "is_ended": rental.is_ended,
        "damage_check": rental.damage_check,
        "has_new_damage": rental.has_new_damage,
        "has_after_photos": has_after_photos,
        "photos_before": photos_before_paths,
        "photos_after": photos_after_paths,
        "damages_before": damages_before_list,
        "damages_after": damages_after_list
    }


# Оновлення кінцевої дати оренди
@router.patch("/update_rental_data_end/{rental_id}")
def update_rental_end_admin(rental_id: int, rental_end: str = Body(embed=True), db: Session = Depends(get_db)):
    rental = db.query(Rental).filter(Rental.rental_id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Оренда не знайдена")
    rental.rental_end = rental_end
    db.commit()
    return {"message": "Дата закінчення оренди оновлена"}


# Страница отчетов
@router.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request, admin: str = Cookie(default=None), db: Session = Depends(get_db)):
    if not admin:
        return RedirectResponse(url="/admin/login")

    rentals = db.query(Rental).all()

    return templates.TemplateResponse("reports.html", {
        "request": request,
        "rentals": rentals
    })

@router.get("/download_rental_report")
def download_rental_report(
    request: Request,
    admin: str = Cookie(default=None),
    db: Session = Depends(get_db),
    rental_id: int = Query(...),
    format: str = Query("csv")
):
    if not admin:
        return RedirectResponse(url="/admin/login")

    rental = db.query(Rental).filter(Rental.rental_id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Оренда не знайдена")

    if format == "csv":
        output = StringIO()
        # Добавляем BOM
        output.write('\ufeff')

        writer = csv.writer(output, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Записываем заголовки
        writer.writerow(["ID", "Користувач", "Автомобіль", "Дата початку", "Дата кінця", "Статус"])

        # Записываем данные аренды
        writer.writerow([rental.rental_id, rental.user.first_name + " " + rental.user.last_name,
                         rental.car.make + " " + rental.car.model, rental.rental_start, rental.rental_end,
                         "Завершено" if rental.is_ended else "Активна"])

        output.seek(0)
        return StreamingResponse(output, media_type="text/csv", headers={
            "Content-Disposition": "attachment; filename=rental_report.csv"
        })


    elif format == "pdf":

        user = rental.user
        car = rental.car

        photos_before = db.query(RentalPhoto).filter(RentalPhoto.rental_id == rental_id,
                                                     RentalPhoto.photo_type.like("before%")).all()
        photos_after = db.query(RentalPhoto).filter(RentalPhoto.rental_id == rental_id,
                                                    RentalPhoto.photo_type.like("after%")).all()

        damages_before = db.query(Damage).join(RentalPhoto).filter(RentalPhoto.rental_id == rental_id,
                                                                   RentalPhoto.photo_type.like("before%")).all()
        damages_after = db.query(Damage).join(RentalPhoto).filter(RentalPhoto.rental_id == rental_id,
                                                                  RentalPhoto.photo_type.like("after%")).all()

        # Генерація PDF
        pdf_file = BytesIO()
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        import os

        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        styles = getSampleStyleSheet()
        styleN = styles["Normal"]
        styleN.fontName = 'DejaVuSans'
        styleN.fontSize = 10
        styleH = styles["Heading1"]
        styleH.fontName = 'DejaVuSans'
        styleH.fontSize = 14

        elements = []
        elements.append(Paragraph(f"Детальний звіт по оренді №{rental.rental_id}", styleH))
        elements.append(Spacer(1, 12))

        # Основна інформація
        data = [
            ["Користувач", f"{user.first_name} {user.last_name}"],
            ["Email", user.email],
            ["Телефон", user.phone],
            ["Telegram ID", user.tg_id or "—"],
            ["Автомобіль", f"{car.make} {car.model} ({car.year})"],
            ["Номерний знак", car.license_plate],
            ["Статус авто", car.status],
            ["Дата початку оренди", str(rental.rental_start)],
            ["Дата завершення", str(rental.rental_end)],
            ["Статус оренди", "Завершено" if rental.is_ended else "Активна"]
        ]
        table = Table(data, colWidths=[150, 350])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 16))

        # Функція для нормалізації шляху до фото
        def normalize_path(path: str) -> str:
            img_path = path.replace("\\", "/")
            return img_path if img_path.startswith("uploads/") else os.path.join("uploads", img_path)

        # Фото ДО оренди
        elements.append(Paragraph("Фото ДО оренди:", styleH))
        for p in photos_before:
            full_img_path = normalize_path(p.photo_path)
            if os.path.exists(full_img_path):
                elements.append(Image(full_img_path, width=250, height=160))
            else:
                elements.append(Paragraph(f"Не знайдено файл: {p.photo_path}", styleN))
            elements.append(Spacer(1, 6))

        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Пошкодження ДО оренди:", styleH))
        for d in damages_before:
            elements.append(Paragraph(f"— {d.damage_type} (довіра: {d.confidence * 100:.1f}%)", styleN))

        elements.append(PageBreak())

        # Фото ПІСЛЯ оренди
        elements.append(Paragraph("Фото ПІСЛЯ оренди:", styleH))
        for p in photos_after:
            full_img_path = normalize_path(p.photo_path)
            if os.path.exists(full_img_path):
                elements.append(Image(full_img_path, width=250, height=160))
            else:
                elements.append(Paragraph(f"Не знайдено файл: {p.photo_path}", styleN))
            elements.append(Spacer(1, 6))

        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Пошкодження ПІСЛЯ оренди:", styleH))
        for d in damages_after:
            elements.append(Paragraph(f"— {d.damage_type} (довіра: {d.confidence * 100:.1f}%)", styleN))

        doc.build(elements)
        pdf_file.seek(0)

        return StreamingResponse(pdf_file, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename=detailed_rental_{rental.rental_id}.pdf"
        })

    else:
        raise HTTPException(status_code=400, detail="Невідомий формат")


