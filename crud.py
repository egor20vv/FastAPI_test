from sqlalchemy.orm import Session
from typing import List, Union

import models
import schemas


def get_user(db: Session, user_id: int) -> models.User:
    """
    Returns user by id

    :param db: current session
    :param user_id: user id
    :return: sought user from model
    :except ValueError: occurs if user is not found by id
    """
    db.query(models.User).exists()
    query = db.query(models.User).filter(models.User.id == user_id).first()
    if not query:
        raise ValueError(f'user with id \'{user_id}\' is not found')
    return query


def get_user_by_nik_name(db: Session, nik_name: str) -> models.User:
    """
    Returns user searching by a nick name\n

    Note nick_name:
    \n format: "@<some nick name>"
    \n example: "@some_user"

    :param db: current session
    :param nik_name: users nick name
    :return: sought user from model
    :except ValueError: occurs if user is not found by nick name
    """
    query = db.query(models.User).filter(models.User.nik_name == nik_name).first()
    if not query:
        raise ValueError(f'user with nickname \'{nik_name}\' is not found')
    return query


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


def post_user(db: Session, user_data: schemas.UserCreate) -> models.User:
    """
    Tries to post user_data into the table via the session (db)

    :param db: current session
    :param user_data: data required to create a user
    :return: created user
    :except ValueError: occurs if user with the given nick name is already taken
    """

    try:
        get_user_by_nik_name(db, user_data.nik_name)
    except Exception as e:
        new_user = models.User(**user_data.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    else:
        raise ValueError(f'This nickname \'{user_data.nik_name}\' is already taken')


def put_user(db: Session, user: models.User, new_user_data: schemas.UserEdit) -> models.User:
    """
    Update user data from the new_user_data

    :param db: current session
    :param user: what to update
    :param new_user_data: new data to update
    :return: updated user
    :except ValueError: occurs if a user is not found in the database
    """

    found_user = db.get(models.User, user.id)
    if found_user is None:
        raise ValueError(f'user is not found in the database')

    keys = user.__dict__.keys()
    for key in keys:
        if not str(key).startswith('_') and hasattr(new_user_data, key):
            new_value = getattr(new_user_data, key)
            setattr(found_user, key, new_value)

    db.commit()
    db.refresh(found_user)
    return found_user


def del_user(db: Session, user: models.User) -> None:
    """
    Deletes user

    :param db: current session
    :param user: user to delete
    :return: None
    :except ValueError: occurs if a user is not found in the database
    """

    found_user = db.get(models.User, user.id)
    if found_user is None:
        raise ValueError(f'user is not found in the database')

    db.delete(found_user)
    db.commit()
