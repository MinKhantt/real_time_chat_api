from fastapi import HTTPException, status


class UserNotFoundError(HTTPException):
    """Raised when a user is not found."""
    
    def __init__(self, detail: str = "User not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class UserEmailExistsError(HTTPException):
    """Raised when trying to create a user with an existing email."""
    
    def __init__(self, detail: str = "User with this email already exists."):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class UserEmailAlreadyRegisteredError(HTTPException):
    """Raised when trying to update a user with an email already registered by another user."""
    
    def __init__(self, detail: str = "Email already registered by another user"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class WeakPasswordError(HTTPException):
    """Raised when password does not meet strength requirements."""
    
    def __init__(self, detail: str = "Password does not meet strength requirements."):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

