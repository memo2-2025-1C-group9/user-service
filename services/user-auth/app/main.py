from fastapi import FastAPI, Request, HTTPException
from app.routers.user_router import router as user_router
from app.db.base import Base
from app.db.session import engine
from app.utils.problem_details import problem_detail_response

app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(user_router, prefix="/api/v1")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return problem_detail_response(
        status_code=exc.status_code,
        title=exc.status_code == 401 and "Unauthorized" or "HTTP Exception",
        detail=exc.detail,
        instance=str(request.url),
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
