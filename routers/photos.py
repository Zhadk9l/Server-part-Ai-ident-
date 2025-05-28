from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from PIL import Image
import io
import uuid
import os
from datetime import datetime
from ultralytics import YOLO
from models import RentalPhoto, Damage
from database import get_db
import cv2


UPLOAD_DIR = "uploads"
model = YOLO("best.pt")

router = APIRouter(
    tags=["Photos and Damage Detection"]
)
def remove_background_opencv(image_path):
    # Завантаження та обробка фото
    image = cv2.imread(image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresholded = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

    # Видалення фону с
    result = cv2.bitwise_and(image, image, mask=thresholded)

    output_path = os.path.join(UPLOAD_DIR, f"processed_{str(uuid.uuid4())}.jpg")
    cv2.imwrite(output_path, result)

    return output_path


@router.post("/process_photo/")
async def process_photo(
    rental_id: int = Form(...),
    user_id: int = Form(...),
    photo_type: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        image_data = await image.read()
        image_file = Image.open(io.BytesIO(image_data))
        # image_file.thumbnail((512, 512))

        image_id = str(uuid.uuid4())
        image_path = os.path.join(UPLOAD_DIR, f"{image_id}.jpg")
        image_file.save(image_path)
        results = model(image_path)
        ignore_classes = ["Broken Light"]
        damages = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls)
                conf = float(box.conf)
                class_name = model.names[cls_id]
                if class_name in ignore_classes:
                    continue
                x1, y1, x2, y2 = map(float, box.xyxy[0])

                damage = Damage(
                    photo_id=None,
                    damage_type=class_name,
                    confidence=round(conf, 2),
                    box=str([x1, y1, x2, y2]),
                    created_at=datetime.now()
                )
                db.add(damage)
                damages.append(damage)

        db_rental_photo = RentalPhoto(
            rental_id=rental_id,
            photo_path=image_path,
            photo_type=photo_type,
            created_at=datetime.now()
        )
        db.add(db_rental_photo)
        db.commit()
        db.refresh(db_rental_photo)

        for damage in damages:
            damage.photo_id = db_rental_photo.photo_id
        db.commit()

        return JSONResponse(content={"message": "Фото успішно оброблено.", "photo_id": db_rental_photo.photo_id})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/get_damages_by_photo")
def get_damages_by_photo(photo_path: str, db: Session = Depends(get_db)):
    photo = db.query(RentalPhoto).filter(RentalPhoto.photo_path.like(f"%{photo_path.split('/')[-1]}")).first()
    if not photo:
        return []
    damages = db.query(Damage).filter(Damage.photo_id == photo.photo_id).all()
    return [{"damage_type": d.damage_type, "confidence": d.confidence, "box": d.box} for d in damages]

@router.get("/get_image/{photo_id}")
async def get_image(photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(RentalPhoto).filter(RentalPhoto.photo_id == photo_id).first()
    if photo:
        return JSONResponse(content={"photo_path": photo.photo_path})
    return JSONResponse(status_code=404, content={"message": "Image not found"})

@router.get("/get_damages_by_rental/{rental_id}/{photo_type}")
def get_damages_by_rental(rental_id: int, photo_type: str, db: Session = Depends(get_db)):
    damage = db.query(Damage).join(RentalPhoto).filter(RentalPhoto.rental_id == rental_id, RentalPhoto.photo_type == photo_type).all()
    return damage
