from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import (
    Message,
    UserList,
    UserPublic,
    UserSchema,
)

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá mundo'}


@app.post('/users/', response_model=UserPublic, status_code=HTTPStatus.CREATED)
def create_user(user: UserSchema, session: Session = Depends(get_session)
                ):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
            )
        )
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists'
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists'
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=user.password
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', response_model=UserList, status_code=HTTPStatus.OK)
def read_users(session: Session = Depends(get_session),
               limit: int = 10,
               offset: int = 0):
    db_users = session.scalars(
        select(User).limit(limit).offset(offset)
    )
    return {'users': db_users}


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(user_id: int,
                user: UserSchema,
                session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND
        )

    user_db.email = user.email
    user_db.password = user.password
    user_db.username = user.username

    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db


@app.delete(
    '/users/{user_id}', response_model=Message
)
def delete_user(user_id: int,
                session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(
            detail='User not found',
            status_code=HTTPStatus.NOT_FOUND
        )

    session.delete(user_db)
    session.commit()

    return {'message': 'User deleted'}


@app.get('/users/{user_id}', response_model=UserPublic)
def read_user(user_id: int,
              session: Session = Depends(get_session)
              ):
    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(
            detail='User not found',
            status_code=HTTPStatus.NOT_FOUND
        )

    return user_db
