from sqlalchemy.orm import Session, Query
from typing import List, Union, Optional, Any

import models
import schemas

from database import SessionLocal

from . import crud_decorators


@crud_decorators.does_raise_error
def get_message(db: Session, message_id, raise_error: bool = True) -> Optional[models.Message]:
    """
    Returns message found by id

    :param db: current session
    :param message_id: message id
    :param raise_error:
        [unnecessary argument]
        if it's True and if am error occurs, function will raise error;
        otherwise if it's False and an error occurs, function will return None

    :return: models.Message only if :param raise_error: is True; otherwise maybe either models.Message or None
    """
    query: Query = db.query(models.Message).filter(models.Message.id == message_id)
    message: Optional[models.Message] = query.first()

    if not raise_error or message is not None:
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