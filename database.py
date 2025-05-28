from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Строка підключения к бд
DATABASE_URL = "mysql+pymysql://root:1234567890-=@localhost/ai_car_rental_system"

# Створення підключення
engine = create_engine(DATABASE_URL, echo=True)

# Ствоернян сесії
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()