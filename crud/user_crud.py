from sqlalchemy.orm import Session
from typing import List, Union

import models
import schemas
from crud import general_crud

from crud.crud_decorators import does_raise_error


@does_raise_error('raise_error')
def get_user(db: Session, user_id: int, **_) -> models.User:
    """
    Returns user by id

    :param db: current session
    :param user_id: user id
    :return: sought user from model
    :except ValueError: occurs if user is not found by id
    """
    user = general_crud.get_item(db, models.User, user_id)

    if user is not None:
        return user
    else:
        raise ValueError(user, f'user is not found by id')


@does_raise_error('raise_error')
def get_user_by_nik_name(db: Session, nik_name: str, **_) -> models.User:
    """
    Returns user searching by a nick name\n

    Note nick_name::

        format: "@<some nick name>"
        example: "@some_user"

    :param db: current session
    :param nik_name: users nick name
    :return: sought user from model
    :except ValueError: occurs if user is not found by nick name
    """
    user = db.query(models.User).filter(models.User.nik_name == nik_name).first()
    if user:
        return user
    else:
        raise ValueError(nik_name, f'user is not found by nick name')


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """
    Returns list of users in range of the skip and the limit

    :param db: current session
    :param skip: from where to start reading users from its table
    :param limit: count of users to return (or less if its fewer)
    :return: list of sought users from model (or empty list if there is no users)
    """

    return db.query(models.User).offset(skip).limit(limit).all()


def get_users_count(db: Session) -> int:
    """
    Returns count of users

    :param db: current session
    :return: count of users
    """
    return db.query(models.User).count()


@does_raise_error('raise_error')
def post_user(db: Session, new_user_data: schemas.User.Create, **_) -> models.User:
    """
    Tries to post user_data into the table via the session (db)

    :param db: current session
    :param new_user_data: data required to create a user
    :return: created user
    :except ValueError: occurs if user with the given nick name is already taken
    """

    try:
        return general_crud.post_item(db, models.User, new_user_data)
    except Exception as e:
        print(e)
        raise ValueError(new_user_data, f'user with that nick name is already created')


@does_raise_error('raise_error')
def put_user(db: Session, user: models.User, new_user_data: schemas.User.Edit, **_) -> models.User:
    """
    Update user data from the new_user_data

    :param db: current session
    :param user: what to update
    :param new_user_data: new data to update
    :return: updated user
    :except ValueError: occurs if a user is not found in the database
    """

    found_user = get_user(db, user.id, raise_error=True)
    try:
        return general_crud.put_item(db, found_user, new_user_data)
    except Exception as e:
        print(e)
        raise ValueError((user, new_user_data,), f'update user with a data error')


@does_raise_error('raise_error')
def del_user(db: Session, user: models.User) -> models.User:
    """
    Deletes user

    :param db: current session
    :param user: user to delete
    :return: None
    :except ValueError: occurs if a user is not found in the database
    """

    found_user = get_user(db, user.id, raise_error=True)
    db.delete(found_user)
    db.commit()
    return found_user

