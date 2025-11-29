from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, server_default="TRUE", nullable=False)
    is_superuser = Column(Boolean, server_default="FALSE", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )

    # For caching and serialization
    def to_dict(self):
        return {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }
    
    def as_dict(self):
        """Alias for to_dict() for compatibility."""
        return self.to_dict()
