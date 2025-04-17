from fastapi import FastAPI, Request, HTTPException
from app.routers.user_router import router as user_router
from app.db.base import Base
from app.db.session import engine
from app.utils.problem_details import problem_detail_response
from sqlalchemy import text

app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(user_router, prefix="/api/v1")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Determinar el título basado en el código de status
    title = "Error de Servidor"
    if exc.status_code == 401:
        title = "No Autorizado"
    elif exc.status_code == 403:
        title = "Prohibido"
    elif exc.status_code == 404:
        title = "No Encontrado"
    elif exc.status_code == 400:
        title = "Solicitud Incorrecta"
    elif exc.status_code == 422:
        title = "Error de Validación"
    elif exc.status_code < 500:
        title = "Error de Cliente"

    return problem_detail_response(
        status_code=exc.status_code,
        title=title,
        detail=exc.detail,
        instance=str(request.url),
        headers=exc.headers if hasattr(exc, "headers") else None,
    )


@app.get("/health")
async def health_check():
    try:
        # Intentar conectar a la base de datos
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
