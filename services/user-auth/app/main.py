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

# Importar todos los modelos para que SQLAlchemy los registre
from app.models.user import User

app = FastAPI()

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Crear todas las tablas al iniciar la aplicación
try:
    Base.metadata.create_all(bind=engine)
    logging.info("Tablas creadas correctamente en la base de datos")
except Exception as e:
    logging.error(f"Error al crear tablas en la base de datos: {str(e)}")
    logging.error(traceback.format_exc())

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

    logging.error(
        f"HTTPException manejada: {exc.detail} (status: {exc.status_code}, url: {request.url})"
    )

    headers = exc.headers or {}

    headers["Content-Type"] = "application/problem+json"

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
    error_type = type(exc).__name__
    
    # Loguear el error completo para debugging interno
    logging.error(f"Excepción no controlada ({error_type}): {str(exc)}")
    logging.error(traceback.format_exc())
    
    # Determinar un mensaje de error apropiado para el usuario
    user_message = "Ha ocurrido un error interno en el servidor"
    
    # Si es un error relacionado con la base de datos, dar un mensaje más específico
    # pero sin exponer detalles internos
    if "sqlalchemy" in error_type.lower() or "psycopg2" in str(exc).lower():
        user_message = "Error al acceder a la base de datos"
    
    return problem_detail_response(
        status_code=500,
        title="Error de Servidor",
        detail=user_message,
        instance=str(request.url),
        headers={"Content-Type": "application/problem+json"},
    )


@app.get("/health")
async def health_check():
    try:

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logging.error(f"Error en health check: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}
