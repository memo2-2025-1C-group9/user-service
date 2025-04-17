from fastapi import FastAPI, Request, HTTPException
from app.routers.user_router import router as user_router
from app.db.base import Base
from app.db.session import engine
from app.utils.problem_details import problem_detail_response
from sqlalchemy import text
import logging
import traceback
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # En producción, cambia esto a las URLs específicas de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

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

    # Añadir log detallado del error
    logging.error(
        f"HTTPException manejada: {exc.detail} (status: {exc.status_code}, url: {request.url})"
    )

    # Asegurar que haya headers adecuados
    headers = exc.headers or {}

    # Importante: Content-Type debe ser application/problem+json para que el cliente lo maneje bien
    headers["Content-Type"] = "application/problem+json"

    # Importante: añadir headers CORS para permitir que el front reciba errores
    headers["Access-Control-Allow-Origin"] = "*"

    return problem_detail_response(
        status_code=exc.status_code,
        title=title,
        detail=exc.detail,
        instance=str(request.url),
        headers=headers,
    )


@app.exception_handler(StarletteHTTPException)
async def starlette_exception_handler(request: Request, exc: StarletteHTTPException):
    """Manejador específico para excepciones de Starlette"""
    return await http_exception_handler(
        request, HTTPException(status_code=exc.status_code, detail=exc.detail)
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejador para errores de validación de petición"""
    logging.error(f"Error de validación: {str(exc)}")
    logging.error(traceback.format_exc())

    # Formatear los errores de validación en un mensaje legible
    error_details = []
    for error in exc.errors():
        loc = " -> ".join([str(x) for x in error.get("loc", [])])
        msg = error.get("msg", "Error de validación")
        error_details.append(f"{loc}: {msg}")

    detail = (
        "; ".join(error_details) if error_details else "Error de validación de datos"
    )

    return problem_detail_response(
        status_code=422,
        title="Error de Validación",
        detail=detail,
        instance=str(request.url),
        headers={"Content-Type": "application/problem+json"},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Manejador para cualquier excepción no controlada"""
    logging.error(f"Excepción no controlada: {str(exc)}")
    logging.error(traceback.format_exc())

    return problem_detail_response(
        status_code=500,
        title="Error de Servidor",
        detail="Ha ocurrido un error interno en el servidor",
        instance=str(request.url),
        headers={"Content-Type": "application/problem+json"},
    )


@app.get("/health")
async def health_check():
    try:
        # Intentar conectar a la base de datos
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logging.error(f"Error en health check: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}
