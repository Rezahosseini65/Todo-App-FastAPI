from fastapi import (
    APIRouter, 
    Path, 
    Depends, 
    HTTPException, 
    status,
    Query
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.core.database import get_db
from app.tasks.models import TaskModel
from app.users.models import User
from app.auths.jwt_auth import get_current_user
from app.tasks.schemas import (
    CreateTaskSchema,
    UpdateTaskSchema,
    ResponseTaskSchema
)

router = APIRouter(tags=['tasks'])


@router.get("/tasks/", response_model=List[ResponseTaskSchema])
async def list_task(
        db: Session = Depends(get_db),
        completed: bool = Query
            (
                None, 
                description="Filter tasks by completion status"
            ),
        limit : int = Query
            (
                default=10, 
                gt=0, 
                le=50, 
                description="Limiting the number of items to retrieve"
            ),
        offset : int = Query(
            default=0,
            ge=0,
            description="Use for paginating based on passed items"
        ),
        user : User = Depends(get_current_user)
    ):
    """
    Retrieve a paginated list of tasks from the database.

    Query Parameters:
    - completed (bool, optional): 
        Filter tasks by their completion status.
        If `true`, only completed tasks are returned. 
        If `false`, only pending tasks are returned. 
        If omitted, all tasks are returned.
    - limit (int, default=10, max=50): 
        Maximum number of tasks to retrieve in a single request.
    - offset (int, default=0): 
        Number of tasks to skip before starting to collect the result set 
        (useful for pagination).

    Returns:
        List[ResponseTaskSchema]: A list of tasks that match the query.
    """


    if completed is not None:
        tasks = db.query(TaskModel).filter_by(is_completed=completed, user_id=user.id)
    else:    
        tasks = db.query(TaskModel).filter_by(user_id=user.id)
    
    tasks = tasks.limit(limit).offset(offset)

    return tasks.all()


@router.get("/tasks/{id}/", response_model=ResponseTaskSchema)
async def detail_task(
    id: int = Path(...), 
    db: Session= Depends(get_db),
    user: User= Depends(get_current_user)
    ):
    """
    Retrieve a specific task by its ID.

    Raises 404 if the task is not found.
    """
    task = db.query(TaskModel).filter_by(id=id, user_id=user.id).one_or_none()

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
async def create_task(
    request: CreateTaskSchema, 
    db: Session = Depends(get_db),
    user: User= Depends(get_current_user)
    ):
    """
    Create a new task.
    Returns the created task or raises 400 if an integrity error occurs.
    """
    data = request.model_dump()
    data.update({"user_id":user.id})
    new_task = TaskModel(**data)
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
async def update_task(
    request: UpdateTaskSchema, 
    id: int = Path(...), 
    db: Session = Depends(get_db),
    user: User= Depends(get_current_user)
    ):
    """
    Update an existing task by its ID.
    Raises 404 if the task is not found.
    """
    task = db.query(TaskModel).filter_by(id=id, user_id=user.id).one_or_none()

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
async def delete_task(
    id: int = Path(...), 
    db: Session = Depends(get_db),
    user: User= Depends(get_current_user)
    ):
    """
    Delete a task by its ID.
    Returns a success message or raises 404 if the task is not found.
    """
    task = db.query(TaskModel).filter_by(id=id, user_id=user.id).one_or_none()

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
