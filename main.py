from typing import List, Optional, IO, Union, Dict, Callable

from fastapi.responses import JSONResponse
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper
from sqlalchemy.orm import Session
import uvicorn

import crud
import models
import schemas
from schemas import ValidationError

from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Dependencies:
    class _SessionContextManager:
        def __init__(self, session: Session = SessionLocal()):
            self.session = session

        def __enter__(self):
            return self.session

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.session.close()

    @classmethod
    def get_db(cls):
        with cls._SessionContextManager() as db:
            yield db

    @classmethod
    def try_to_get_user_id(cls, user_identifier: Union[int, str]) -> int:
        try:
            with cls._SessionContextManager() as _db:
                user = crud.get_user(_db, user_identifier) \
                    if type(user_identifier) is int \
                    else crud.get_user_by_nik_name(_db, user_identifier)
                return user.id
        except ValueError as e:  # User is not found exception
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={'message': str(e)}
            )

    @classmethod
    def complete_user_edit(cls, new_user_data: Union[schemas.UserEdit, dict]) -> \
            Callable[[models.User], schemas.UserEdit]:
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

        def wrapper(user: models.User) -> Union[schemas.UserEdit, JSONResponse]:
            try:
                if cls._new_user_data.__class__ is dict:
                    return schemas.UserEdit(**_complete_user_edit(cls._new_user_data, user))
                else:
                    return cls._new_user_data

            except ValidationError as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=e.errors()
                )

        return wrapper


@app.get('/', response_model=dict)
def root():
    return {'Main Page': True}


@app.get('/users/', response_model=List[schemas.User], status_code=status.HTTP_200_OK)
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(Dependencies.get_db)):
    users = crud.get_users(db, skip, limit)
    return users


@app.get('/users/count', response_model=Dict[str, int], status_code=status.HTTP_200_OK)
def get_users_count(db: Session = Depends(Dependencies.get_db)):
    return {'Count of users': crud.get_users_count(db)}


@app.get('/users/{user_identifier}', response_model=schemas.User, status_code=status.HTTP_200_OK)
def get_user(
        user_id: int = Depends(Dependencies.try_to_get_user_id),
        db: Session = Depends(Dependencies.get_db)
):
    return crud.get_user(db, user_id)  # try_to_get_user(db, user_identifier)


@app.post('/users/', response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def post_user(user_data: schemas.UserCreate, db: Session = Depends(Dependencies.get_db)):
    try:
        return crud.post_user(db, user_data=user_data)
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'message': str(e)
            }
        )


@app.put('/users/{user_identifier}', response_model=schemas.User, status_code=status.HTTP_200_OK)
def put_user(
        user_id: int = Depends(Dependencies.try_to_get_user_id),
        fun_complete_user_edit: Callable[[models.User], schemas.UserEdit] = Depends(Dependencies.complete_user_edit),
        db: Session = Depends(Dependencies.get_db)
):
    # Try to update user
    user = crud.get_user(db, user_id)
    new_user_data = fun_complete_user_edit(user)
    try:
        return crud.put_user(db, user=user, new_user_data=new_user_data)
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'type': 'db crashed (i guess)',
                'details': 'check logs'
            }
        )


# @app.delete('/users/{user_identifier}', response_model=schemas.User, status_code=status.HTTP_200_OK)
# def delete_user(
#         user_id: int = Depends(Dependencies.try_to_get_user_id),
#         db: Session = Depends(Dependencies.get_db)
# ):
#      pass


if __name__ == '__main__':
    uvicorn.run("main:app", port=5000, reload=True, access_log=False)
    # app.get('/users/', response_model=List[schemas.User], status_code=status.HTTP_200_OK)(schema_validator)()
