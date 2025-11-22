from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import authenticate_user, create_token_for_user
from app.db.database import async_session  



async def login_for_access_token_service(
    session: async_session,  
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await authenticate_user(session, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return create_token_for_user(user)
