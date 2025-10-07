from passlib.context import CryptContext

from sqlalchemy import(
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    func
)
from sqlalchemy.orm import relationship

from app.core.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    username = Column(
        String(255),
        nullable=False,
        unique=True
    )
    password = Column(
        String,
        nullable=False
    )
    is_active = Column(
        Boolean,
        default=True
    )
    created_at = Column(
        DateTime,
        server_default=func.now()
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        server_onupdate=func.now()
    )

    tasks = relationship("TaskModel", back_populates="user")


    def __repr__(self):
        return f'id={self.id!r}--username={self.username!r}'
    
    def hash_password(self, plain_password: str) -> str:
        """Hashes the given password using bcrypt."""
        return pwd_context.hash(plain_password)
        
    def set_password(self, plain_text: str) -> None:
        """
        Hashes the given plain-text password and stores it in the `password` field.
        The raw password is never saved directly.
        """
        self.password = self.hash_password(plain_text)
    
    

