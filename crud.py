from sqlalchemy.orm import Session
from typing import List, Union

import models
import schemas


def get_user(db: Session, user_id: int) -> models.User:
    query = db.query(models.User).filter(models.User.id == user_id).first()
    if not query:
        raise ValueError(f'user with id \'{user_id}\' is not found')
    return query


def get_user_by_nik_name(db: Session, nik_name: str) -> models.User:
    query = db.query(models.User).filter(models.User.nik_name == nik_name).first()
    if not query:
        raise ValueError(f'user with nickname \'{nik_name}\' is not found')
    return query


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def get_users_count(db: Session) -> int:
    return db.query(models.User).count()


def post_user(db: Session, user_data: schemas.UserCreate) -> models.User:
    try:
        get_user_by_nik_name(db, user_data.nik_name)
    except Exception as e:
        new_user = models.User(
            nik_name=user_data.nik_name,
            fst_name=user_data.fst_name,
            sec_name=user_data.sec_name
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    else:
        raise ValueError(f'This nickname \'{user_data.nik_name}\' is already taken')


def put_user(db: Session, user: models.User, new_user_data: schemas.UserEdit) -> models.User:
    keys = user.__dict__.keys()
    for key in keys:
        if not str(key).startswith('_') and hasattr(new_user_data, key):
            new_value = getattr(new_user_data, key)
            setattr(user, key, new_value)

    db.commit()
    db.refresh(user)
    return user


def del_user(db: Session, user: models.User) -> None:
    db.delete(user)
    db.commit()