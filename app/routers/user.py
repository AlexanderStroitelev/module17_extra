from typing import Annotated

from fastapi import APIRouter , Depends , status , HTTPException
from slugify import slugify
from sqlalchemy import insert , select , update , delete
from sqlalchemy.orm import Session

from app.backend.db_depends import get_db
from app.models.user import User
from app.models.task import Task
from app.schemas import CreateUser , UpdateUser


router = APIRouter ( )


@router.get ( "/" )
async def all_users ( db: Annotated [ Session , Depends ( get_db ) ] ) :
    query = select ( User )
    result = db.scalars ( query ).all ( )
    return result


@router.get ( "/{user_id}" )
async def user_by_id ( user_id: int , db: Annotated [ Session , Depends ( get_db ) ] ) :
    query = select ( User ).where ( User.id == user_id )
    user = db.scalars ( query ).first ( )
    if user is not None :
        return user
    raise HTTPException ( status_code = status.HTTP_404_NOT_FOUND , detail = "User was not found" )


@router.post ( "/create" )
async def create_user ( user: CreateUser , db: Annotated [ Session , Depends ( get_db ) ] ) :
    existing_user = db.scalars ( select ( User ).where ( User.username == user.username ) ).first ( )
    if existing_user :
        raise HTTPException ( status_code = status.HTTP_400_BAD_REQUEST , detail = "Username already exists" )
    user_data = user.model_dump ( )
    user_data [ "slug" ] = slugify ( user.username )
    query = insert ( User ).values ( **user_data )
    db.execute ( query )
    db.commit ( )
    return { "status_code" : status.HTTP_201_CREATED , "transaction" : "Successful" }



@router.put ( "/update/{user_id}" )
async def update_user ( user_id: int , user: UpdateUser , db: Annotated [ Session , Depends ( get_db ) ] ) :
    query = select ( User ).where ( User.id == user_id )
    existing_user = db.scalars ( query ).first ( )
    if existing_user :
        update_query = (
            update ( User )
            .where ( User.id == user_id )
            .values ( **user.model_dump ( ) )
        )
        db.execute ( update_query )
        db.commit ( )
        return { "status_code" : status.HTTP_200_OK , "transaction" : "User update is successful!" }
    raise HTTPException ( status_code = status.HTTP_404_NOT_FOUND , detail = "User was not found" )



@router.delete("/delete/{user_id}")
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    query = select(User).where(User.id == user_id)
    existing_user = db.scalars(query).first()
    if existing_user:
        delete_tasks_query = delete(Task).where(Task.user_id == user_id)
        db.execute(delete_tasks_query)
        delete_user_query = delete(User).where(User.id == user_id)
        db.execute(delete_user_query)
        db.commit()
        return {"status_code": status.HTTP_200_OK, "transaction": "User deletion is successful!"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")


@router.get("/{user_id}/tasks")
async def tasks_by_user_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    query = select(Task).where(Task.user_id == user_id)
    tasks = db.scalars(query).all()
    return tasks
