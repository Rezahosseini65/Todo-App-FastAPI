from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class TaskBaseSchema(BaseModel):
    """
    Base schema for defining a task.
    Includes the title, description, and completion status.
    """
    title: str = Field(
        ...,
        max_length=64,
        description="Title of the task (maximum 64 characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Detailed description of the task (optional, maximum 500 characters)"
    )
    is_completed: bool = Field(
        ...,
        description="Completion status of the task (True = completed, False = not completed)"
    )


class CreateTaskSchema(TaskBaseSchema):
    """
    Schema for creating a new task.
    Inherits all fields from TaskBaseSchema.
    """
    pass


class UpdateTaskSchema(TaskBaseSchema):
    """
    Schema for updating an existing task.
    Inherits all fields from TaskBaseSchema.
    """
    pass


class ResponseTaskSchema(TaskBaseSchema):
    """
    Schema for returning task data in API responses.
    Extends TaskBaseSchema with ID and timestamps.
    """
    id: int = Field(
        ...,
        description="Unique identifier of the task"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the task was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp of the most recent update to the task"
    )
