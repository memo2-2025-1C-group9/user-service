from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://test_db_e0tq_user:aARRiPFXHlp9D7sbRLds44lNgOSwGp2F@dpg-cvt6a649c44c73ccrhu0-a.oregon-postgres.render.com:5432/test_db_e0tq?sslmode=require"
    )


settings = Settings()
