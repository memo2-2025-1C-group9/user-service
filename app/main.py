import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import uvicorn
import re
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError



app = FastAPI()

# Configuración de la base de datos
DATABASE_URL = "postgresql://user:password@db:5432/student_management"
Base = declarative_base()

# Intentar conectarse a la base de datos con reintentos
def wait_for_db_connection(retries=5, delay=2):
    for attempt in range(retries):
        try:
            engine = create_engine(DATABASE_URL)
            engine.connect()
            return engine
        except Exception as e:
            print(f"Intento {attempt + 1} de {retries}: No se pudo conectar a la base de datos. Reintentando en {delay} segundos...")
            time.sleep(delay)
    raise Exception("No se pudo conectar a la base de datos después de varios intentos.")

engine = wait_for_db_connection()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modelo de usuario
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    def validate_password(cls, password):
        if len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        if not password.isalnum():
            raise ValueError("La contraseña debe ser alfanumérica.")
        return password

    @field_validator("name")
    def validate_name(cls, name):
        if not re.match("^[a-zA-Z0-9 ]+$", name):
            raise ValueError("El nombre no puede contener caracteres especiales.")
        return name


@app.post("/register")
def register_user(user: UserCreate):
    db = SessionLocal()
    try:
        new_user = User(name=user.name, email=user.email)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"status": "success", "user_id": new_user.id}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")
    finally:
        db.close()

# Función para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)