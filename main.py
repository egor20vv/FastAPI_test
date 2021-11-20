from typing import List, Optional, Union, Dict, Callable, Generator, Any

from fastapi.responses import JSONResponse
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
import uvicorn

import models
from crud import user_crud, message_crud
# from schemas import Message, User
import schemas


from database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Dependencies:
    """
    Static class contains dependencies

    Example::

        Depends(Dependencies.<some_method>)

    """
    class RoutingConstants:
        user_identifier = "user_identifier"

    class _SessionContextManager:
        def __init__(self, session: Session = SessionLocal()):
            self.session = session

        def __enter__(self):
            return self.session

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.session.close()

    @classmethod
    def get_db(cls) -> Generator[Session, Any, None]:
        """
        The generator returning a session
        """

        with cls._SessionContextManager() as db:
            yield db

    @classmethod
    def try_to_get_user_id(cls, user_identifier: Union[int, str]) -> int:
        """
        Tries to return the user_id found by user_identifier, which is user_id or user_nick_name\n
        Otherwise raises a error

        :param user_identifier: union[user_id: int, user_nick_name: string]
        :return: found user_id
        :except HTTPException: 404 (user is not found)
        """
        try:
            with cls._SessionContextManager() as _db:
                user = user_crud.get_user(_db, user_identifier) \
                    if type(user_identifier) is int \
                    else user_crud.get_user_by_nik_name(_db, user_identifier)
                return user.id
        except ValueError as e:  # User is not found exception
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={'message': str(e)}
            )

    @classmethod
    def complete_user_edit(cls, new_user_data: Union[schemas.User.Edit, dict]) -> \
            Callable[[models.User], schemas.User.Edit]:
        """
        Returns a function that returns UserEdit independent of a value and both possible taken new_user_data types \n
        ____

        Example of use::

            fun: Callable[[models.User], schemas.UserEdit]
            some_user_data: Union[schemas.UserEdit, dict] = {}
            fun = Depends(Dependencies.complete_user_edit(some_user_data))

        :param new_user_data: is a schema of UserEdit or dict with incomplete data of UserEdit
        :return: fun(user: models.User) -> schemas.UserEdit
        :except HTTPException: [raises form the returned function] occurs if passed
            argument (user: models.User or new_user_data: as dict [from "parent" function]) will contain some
            unacceptable to validate data
        """
        cls._new_user_data = new_user_data

        def _complete_user_edit(new_data: dict, old_data):
            new_data_keys = new_data.keys()
            old_data_keys = old_data.__dict__.keys()

            for old_data_key in old_data_keys:
                if not str(old_data_key).startswith('_') and old_data_key not in new_data_keys:
                    new_value = getattr(old_data, old_data_key)
                    # setattr(new_data, str(old_data_key), new_value)
                    new_data[str(old_data_key)] = new_value
                    # new_data[str(old_data_key)] = old_data.__getattribute__(old_data_key)

            return new_data

        def wrapper(user: models.User) -> schemas.User.Edit:
            try:
                if cls._new_user_data.__class__ is dict:
                    return schemas.User.Edit(**_complete_user_edit(cls._new_user_data, user))
                else:
                    return cls._new_user_data

            except ValidationError as e:  # Validation error occurs
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=e.errors()
                )

        return wrapper


@app.get('/', response_model=dict)
def root():
    return {'Main Page': True}


@app.get('/users/', response_model=List[schemas.User.Get], status_code=status.HTTP_200_OK)
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(Dependencies.get_db)):
    users = user_crud.get_users(db, skip, limit)
    return users


@app.get('/users/count', response_model=Dict[str, int], status_code=status.HTTP_200_OK)
def get_users_count(db: Session = Depends(Dependencies.get_db)):
    return {'Count of users': user_crud.get_users_count(db)}


@app.get('/users/{' + Dependencies.RoutingConstants.user_identifier + '}',
         response_model=schemas.User.Get,
         status_code=status.HTTP_200_OK)
def get_user(
        user_id: int = Depends(Dependencies.try_to_get_user_id),
        db: Session = Depends(Dependencies.get_db)
):
    return user_crud.get_user(db, user_id)


@app.post('/users/', response_model=schemas.User.Get, status_code=status.HTTP_201_CREATED)
def post_user(user_data: schemas.User.Create, db: Session = Depends(Dependencies.get_db)):
    try:
        return user_crud.post_user(db, user_data=user_data)
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'message': str(e)
            }
        )


@app.put('/users/{' + Dependencies.RoutingConstants.user_identifier + '}',
         response_model=schemas.User.Get,
         status_code=status.HTTP_200_OK)
def put_user(
        user_id: int = Depends(Dependencies.try_to_get_user_id),
        fun_complete_user_edit: Callable[[models.User], schemas.User.Edit] = Depends(Dependencies.complete_user_edit),
        db: Session = Depends(Dependencies.get_db)
):
    # Try to update user
    user = user_crud.get_user(db, user_id)
    new_user_data = fun_complete_user_edit(user)
    return user_crud.put_user(db, user=user, new_user_data=new_user_data)


@app.delete('/users/{user_identifier}', response_model=schemas.User.Get, status_code=status.HTTP_200_OK)
def delete_user(
        user_id: int = Depends(Dependencies.try_to_get_user_id),
        db: Session = Depends(Dependencies.get_db)
):
    user_to_del = user_crud.get_user(db, user_id)
    user_crud.del_user(db, user_to_del)


if __name__ == '__main__':
    uvicorn.run("main:app", port=5000, reload=True, access_log=False)
