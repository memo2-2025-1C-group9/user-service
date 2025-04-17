from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from fastapi import HTTPException, status
from app.repositories.user_repository import get_user_by_email
from app.schemas.user import UserLogin, Token
from app.models.user import User
from app.core.security import create_access_token
from app.core.config import settings
import logging

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
        user = get_user_by_email(db, email)
        if not user:
            return False

        if user.is_blocked:
            # si esta bloqueada por tiempo, debo de verificar si el tiempo de bloqueo ya paso
            if user.blocked_until and user.blocked_until < datetime.now():
                # si el tiempo de bloqueo ha pasado, lo desbloqueo y reseteo los intentos fallidos
                try:
                    user.is_blocked = False
                    reset_failed_attempts(user, db)
                except Exception as e:
                    db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error al desbloquear usuario: {str(e)}",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                # si el tiempo de bloqueo no ha pasado, sigue bloqueado
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Usuario bloqueado",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        if not user.password == password:
            # si la contraseña no es valida, le sumo un intento fallido
            try:
                # si es el primer intento fallido, le guardo la fecha y hora
                if (
                    (not user.first_login_failure)
                    or user.first_login_failure + LOCK_TIME_LOGIN_WINDOW
                    < datetime.now()
                ):  # la ventana de tiempo no existe o ya paso
                    user.failed_login_attempts = 0
                    user.first_login_failure = datetime.now()

                # si no entra al if, significa que esta dentro de la ventana de tiempo
                user.failed_login_attempts += 1
                db.add(user)
                db.commit()

                if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                    # si el numero de intentos fallidos es mayor o igual al maximo, lo bloqueo
                    block_user(user, db)
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Usuario bloqueado por múltiples intentos fallidos",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            except HTTPException as e:
                # Reenvía la excepción HTTP si es una que hemos creado
                raise e
            except Exception as e:
                # Si hay un error en la operación de DB, hacemos rollback y lanzamos excepción controlada
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al procesar credenciales: {str(e)}",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return False

        # si la contraseña es correcta, reseteo los intentos fallidos
        try:
            reset_failed_attempts(user, db)
        except Exception as e:
            db.rollback()
            # No lanzamos excepción aquí porque el login sigue siendo válido
            # Solo avisamos del error pero permitimos continuar
            logging.error(f"Error al resetear intentos fallidos: {str(e)}")

        return user
    except HTTPException as e:
        # Reenvía la excepción HTTP si es una que hemos creado
        raise e
    except Exception as e:
        # Para cualquier otra excepción, devolvemos un error controlado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en autenticación: {str(e)}",
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
        # Reenvía la excepción HTTP si es una que hemos creado
        raise e
    except Exception as e:
        logging.error(f"Error en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
            headers={"WWW-Authenticate": "Bearer"},
        )
