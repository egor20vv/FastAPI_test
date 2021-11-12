from sqlalchemy.orm import Session, Query
from typing import List, Union, Optional, Any

import models
import schemas

from database import SessionLocal

from crud.crud_decorators import does_raise_error


@does_raise_error('raise_error')
def get_message(db: Session, message_id, **_) -> Optional[models.Message]:
    """
    Returns message found by id

    :param db: current session
    :param message_id: message id

    :return: models.Message or None
    :except ValueError: if message was not found
    """
    query: Query = db.query(models.Message).filter(models.Message.id == message_id)
    message: Optional[models.Message] = query.first()

    if message is not None:
        return message
    else:
        raise ValueError(f'message with id \'{message_id}\' is not found')

#
# def post_message(db: Session, new_message_data: schemas.MessageCreate, raise_error: bool = True) -> models.Message:
#     pass


if __name__ == '__main__':
    try:
        mess = get_message(SessionLocal(), 1)
        print(mess)
    except Exception as e:
        print(e)