from fastapi import FastAPI
from app.routers.user_router import router as user_router
from app.db.base import Base
from app.db.session import engine

app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(user_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}