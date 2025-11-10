from fastapi import FastAPI

from app.routes import user, auth
from app.core.config import settings

app = FastAPI(
    title="Real Time Chat Application API",
    description="API for a real-time chat application built with FastAPI.",
    version="1.0.0"
)

app.include_router(user.router, prefix=settings.API_PREFIX)
app.include_router(auth.router, prefix=settings.API_PREFIX)

@app.get("/")
async def read_root():
    return {"Hello": "World"}



