from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import user, auth
from app.core.config import settings

app = FastAPI(
    title="Real Time Chat Application API",
    description="API for a real-time chat application built with FastAPI.",
    version="1.0.0"
)

app.include_router(user.router, prefix=settings.API_PREFIX)
app.include_router(auth.router, prefix=settings.API_PREFIX)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://192.168.100.8:port"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"Hello": "World"}



