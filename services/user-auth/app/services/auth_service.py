from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from fastapi import HTTPException, status
from app.repositories.user_repository import get_user_by_email
from app.schemas.user import UserLogin, Token, ServiceLogin
from app.models.user import User
from app.core.security import create_access_token
from app.core.config import settings
import logging
import traceback

LOCK_TIME_LOGIN_WINDOW = timedelta(minutes=settings.LOCK_TIME_LOGIN_WINDOW)
LOCK_USER_TIME = timedelta(minutes=settings.LOCK_USER_TIME)


def reset_failed_attempts(user: User, db: Session):
    user.failed_login_attempts = 0
    user.first_login_failure = None
    db.add(user)
    db.commit()


def block_user(user: User, db: Session):
    user.is_blocked = True
    user.blocked_until = datetime.now() + LOCK_USER_TIME
    user.failed_login_attempts = 0
    db.add(user)
    db.commit()


def authenticate_user(db: Session, email: str, password: str):
    try:
        logging.info(f"Intentando autenticar usuario con email: {email}")

        try:
            user = get_user_by_email(db, email)
        except Exception as db_error:
            logging.error(f"Error de base de datos: {str(db_error)}")
            logging.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al conectar con la base de datos",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user:
            logging.info(f"Usuario con email {email} no encontrado")
            return False

        if user.is_blocked:
            if user.blocked_until and user.blocked_until < datetime.now():
                try:
                    logging.info(f"Desbloqueando usuario: {email}")
                    user.is_blocked = False
                    reset_failed_attempts(user, db)
                except Exception as e:
                    logging.error(f"Error al desbloquear usuario: {str(e)}")
                    db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Error al procesar la solicitud",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                logging.warning(f"Intento de login con usuario bloqueado: {email}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Usuario bloqueado",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        if not user.password == password:
            try:
                logging.info(f"Contraseña incorrecta para: {email}")
                if (
                    (not user.first_login_failure)
                    or user.first_login_failure + LOCK_TIME_LOGIN_WINDOW
                    < datetime.now()
                ):
                    user.failed_login_attempts = 0
                    user.first_login_failure = datetime.now()
                    logging.info(
                        f"Primer intento fallido o fuera de ventana para: {email}"
                    )

                user.failed_login_attempts += 1
                logging.info(
                    f"Incrementando intentos fallidos para {email}: {user.failed_login_attempts}"
                )
                db.add(user)
                db.commit()

                if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                    logging.warning(
                        f"Bloqueando usuario por múltiples intentos: {email}"
                    )
                    block_user(user, db)
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Usuario bloqueado por múltiples intentos fallidos",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            except HTTPException as e:
                raise e
            except Exception as e:
                logging.error(f"Error al registrar intento fallido: {str(e)}")
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al procesar la solicitud",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return False

        try:
            logging.info(f"Login exitoso para: {email}")
            reset_failed_attempts(user, db)
        except Exception as e:
            db.rollback()
            logging.error(f"Error al resetear intentos fallidos: {str(e)}")

        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error no controlado en autenticación: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error en el servicio de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )


def login_user(db: Session, credentials: UserLogin):
    try:
        user = authenticate_user(db, credentials.email, credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            access_token_expires = timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            access_token = create_access_token(
                data={"sub": user.email}, expires_delta=access_token_expires
            )
            return Token(access_token=access_token, token_type="bearer")
        except Exception as e:
            logging.error(f"Error al generar token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al generar token de acceso",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
            headers={"WWW-Authenticate": "Bearer"},
        )


def authenticate_service(user: str, password: str):
    if user == settings.SERVICE_USERNAME and password == settings.SERVICE_PASSWORD:
        logging.info(f"Login exitoso para servicio")
        return True
    else:
        logging.info(f"Contraseña incorrecta para servicio")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )


def login_service(credentials: ServiceLogin):
    try:
        if authenticate_service(credentials.user, credentials.password):
            access_token_expires = timedelta(
                minutes=settings.SERVICE_ACCESS_TOKEN_EXPIRE_MINUTES
            )
            access_token = create_access_token(
                data={"service": credentials.user}, expires_delta=access_token_expires
            )
            return Token(access_token=access_token, token_type="bearer")
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error en login de servicio")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
            headers={"WWW-Authenticate": "Bearer"},
        )
