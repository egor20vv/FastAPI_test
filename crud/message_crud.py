from sqlalchemy.orm import Session, Query
from typing import List, Union, Optional, Any

import models
import schemas

from database import SessionLocal

from crud.crud_decorators import does_raise_error
import general_crud


@does_raise_error('raise_error')
def get_message(db: Session, message_id, **_) -> models.Message:
    """
    Returns message found by id

    :param db: current session
    :param message_id: message id

    :return: models.Message or None
    :except ValueError: if message was not found
    """
    message = general_crud.get_item(db, models.Message, message_id)

    if message is not None:
        return message
    else:
        raise ValueError(message_id, f'message is not found by id')


@does_raise_error('raise_error')
def post_message(db: Session, new_message_data: schemas.Message.Create, **_) -> models.Message:
    try:
        return general_crud.post_item(db, models.Message, new_message_data)
    except Exception as e:
        print(e)
        raise ValueError(new_message_data, f'message creation error')


@does_raise_error('raise_error')
def put_message(db: Session, message: models.Message, new_message_data: schemas.Message.Edit, **_) -> models.Message:
    found_message = get_message(db, message.id, raise_error=True)
    try:
        return general_crud.put_item(db, found_message, new_message_data)
    except Exception as e:
        print(e)
        raise ValueError((message, new_message_data,), f'update message with a data error')


@does_raise_error('raise_error')
def del_message(db: Session, message: models.Message) -> models.Message:
    found_message = get_message(db, message.id, raise_error=True)
    db.delete(found_message)
    db.commit()
    return found_message


if __name__ == '__main__':
    try:
        mess = post_message(SessionLocal(), schemas.Message.Create())
        print(mess)
    except Exception as e:
        print(e)