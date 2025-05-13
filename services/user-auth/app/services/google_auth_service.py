from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.user_repository import get_user_by_email, create_user_google
from app.core.security import create_user_jwt
from app.schemas.user import UserCreateGoogle
from google.oauth2 import id_token
from google.auth.transport import requests
from app.models.user import AuthProvider
import logging
from app.core.config import settings


def google_login_user(db: Session, token: str):
    try:
        logging.info(f"Validando google token")
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), settings.WEB_CLIENT_ID
        )
        print(idinfo)
        user_email = idinfo["email"]

        logging.info(f"Intentando autenticar usuario google con email: {user_email}")

        user = get_user_by_email(db, user_email)

        if not user:
            logging.info(f"Email: {user_email} no registrado, creando cuenta")
            create_user_google(
                db,
                UserCreateGoogle(
                    name=idinfo["name"],
                    email=user_email,
                    password=token,
                    auth_provider=AuthProvider.GOOGLE,
                ),
            )
            return create_user_jwt(user_email)

        if user.auth_provider in (AuthProvider.GOOGLE, AuthProvider.LOCAL_GOOGLE):
            logging.info(f"Login con google exitoso para: {user_email}")
            return create_user_jwt(user_email)
        else:
            logging.info(
                f"Email: {user_email} registrado, sin login con google, combinar informacion"
            )
            # NO tiene login con google
            return {"sincronize": True}  # TODO: Ver como manejarse con el frontend

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )
