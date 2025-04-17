from app.db.session import SessionLocal
from fastapi import HTTPException
import logging


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error real de conexión a DB: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error de conexión a la base de datos"
        )
    finally:
        if db:
            try:
                db.close()
            except Exception as e:
                logging.error(f"Error al cerrar conexión DB: {str(e)}")
