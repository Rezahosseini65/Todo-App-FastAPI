from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Boolean, 
    func, 
    Text, 
    DateTime
)

from app.core.database import Base


class TaskModel(Base):
    __tablename__="tasks"

    id = Column(
        Integer, 
        primary_key=True,
        autoincrement=True 
    )
    title = Column(
        String(64),
        nullable=False
    )
    description = Column(
        Text(500),
        nullable=True
    )
    is_completed = Column(
        Boolean,
        default=False
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

    def __repr__(self):
        return f'Task(id={self.id}, title={self.title}, is_done={self.is_completed})'