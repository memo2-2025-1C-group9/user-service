from app.db.session import SessionLocal
from fastapi import HTTPException


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error de conexión a la base de datos: {str(e)}"
        )
    finally:
        if db:
            try:
                db.close()
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Error al cerrar la conexión: {str(e)}"
                )
