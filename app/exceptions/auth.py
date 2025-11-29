from fastapi import HTTPException, status


class InvalidCredentialsError(HTTPException):
    """Raised when credentials cannot be validated."""
    
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class IncorrectCredentialsError(HTTPException):
    """Raised when username or password is incorrect."""
    
    def __init__(self, detail: str = "Incorrect username or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InactiveUserError(HTTPException):
    """Raised when trying to access with an inactive user account."""
    
    def __init__(self, detail: str = "Inactive user"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

