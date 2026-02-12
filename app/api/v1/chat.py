from fastapi import APIRouter

from . import chat_group, chat_one_to_one, chat_ws


router = APIRouter()
router.include_router(chat_one_to_one.router)
router.include_router(chat_group.router)
router.include_router(chat_ws.router)
