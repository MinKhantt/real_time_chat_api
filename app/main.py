from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import user, auth
from app.core.config import settings

app = FastAPI(
    title="Real Time Chat Application API",
    description="API for a real-time chat application built with FastAPI.",
    version="1.0.0",
)

api_prefix_v1 = f"{settings.API_PREFIX}{settings.API_V1}"
app.include_router(user.router, prefix=api_prefix_v1)
app.include_router(auth.router, prefix=api_prefix_v1)

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

def write_notification(email: str, message=""):
    with open("app/test.txt", "a") as email_file:
        content = f"Notification for {email}: {message}\n"
        email_file.write(content)

@app.post("/sent-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="blah blah")
    return {"message": "Notification sent in the background"}


