from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import Session

from app.backend.db_depends import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas import CreateTask, UpdateTask
from slugify import slugify


router = APIRouter()


@router.get("/")
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    query = select(Task)
    result = db.scalars(query).all()
    return result


@router.get("/{task_id}")
async def task_by_id(task_id: int, db: Annotated[Session, Depends(get_db)]):
    query = select(Task).where(Task.id == task_id)
    task = db.scalars(query).first()
    if task is not None:
        return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")


@router.post("/create")
async def create_task(task: CreateTask, user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
    task_data = task.model_dump()
    task_data["user_id"] = user_id
    task_data["slug"] = slugify(task.title)
    query = insert(Task).values(**task_data)
    db.execute(query)
    db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.put("/update/{task_id}")
async def update_task(task_id: int, task: UpdateTask, db: Annotated[Session, Depends(get_db)]):
    query = select(Task).where(Task.id == task_id)
    existing_task = db.scalars(query).first()
    if existing_task:
        update_query = (update(Task).where(Task.id == task_id).values(**task.model_dump()))
        db.execute(update_query)
        db.commit()
        return {"status_code": status.HTTP_200_OK, "transaction": "Task update is successful!"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")


@router.delete("/delete/{task_id}")
async def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    query = select(Task).where(Task.id == task_id)
    existing_task = db.scalars(query).first()
    if existing_task:
        delete_query = delete(Task).where(Task.id == task_id)
        db.execute(delete_query)
        db.commit()
        return {"status_code": status.HTTP_200_OK, "transaction": "Task deletion is successful!"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")
