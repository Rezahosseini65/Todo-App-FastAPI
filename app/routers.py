from fastapi import (
    APIRouter, 
    Path, 
    Depends, 
    HTTPException, 
    status
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.core.database import get_db
from app.models import TaskModel
from app.schemas import (
    CreateTaskSchema,
    UpdateTaskSchema,
    ResponseTaskSchema
)

router = APIRouter(tags=['tasks'])


@router.get("/tasks/", response_model=List[ResponseTaskSchema])
async def list_task(db: Session = Depends(get_db)):
    """
    Retrieve all tasks from the database.
    """
    tasks = db.query(TaskModel).all()
    return tasks


@router.get("/tasks/{id}/", response_model=ResponseTaskSchema)
async def detail_task(id: int = Path(...), db: Session = Depends(get_db)):
    """
    Retrieve a specific task by its ID.

    Raises 404 if the task is not found.
    """
    task = db.query(TaskModel).filter_by(id=id).one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Task with ID {id} not found",
                "suggestion": "Check available tasks at /tasks/"
            }
        )
    
    return task


@router.post("/tasks/", response_model=ResponseTaskSchema, status_code=status.HTTP_201_CREATED)
async def create_task(request: CreateTaskSchema, db: Session = Depends(get_db)):
    """
    Create a new task.
    Returns the created task or raises 400 if an integrity error occurs.
    """
    new_task = TaskModel(**request.model_dump())
    db.add(new_task)

    try:
        db.commit()
        db.refresh(new_task)
        return new_task
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Task creation failed - integrity error",
                "errors": str(e.orig)
            }
        )
    

@router.put("/tasks/{id}/", response_model=ResponseTaskSchema)
async def update_task(request: UpdateTaskSchema, id: int = Path(...), db: Session = Depends(get_db)):
    """
    Update an existing task by its ID.
    Raises 404 if the task is not found.
    """
    task = db.query(TaskModel).filter_by(id=id).one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Task with ID {id} not found",
                "suggestion": "Check available tasks at /tasks/"
            }
        )
    
    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task


@router.delete("/tasks/{id}/")
async def delete_task(id: int = Path(...), db: Session = Depends(get_db)):
    """
    Delete a task by its ID.
    Returns a success message or raises 404 if the task is not found.
    """
    task = db.query(TaskModel).filter_by(id=id).one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Task with ID {id} not found",
                "suggestion": "Check available tasks at /tasks/"
            }
        )

    db.delete(task)
    db.commit()

    return {"message": "task removed successfully"}
