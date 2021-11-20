from pydantic import BaseModel
from sqlalchemy.orm import Session

import schemas
from database import Base


def get_item(db: Session, model, item_id: int):
    return db.get(model, item_id)


def post_item(db: Session, model, new_item_data: BaseModel):
    item = model(**new_item_data.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def put_item(db: Session, item: Base, new_item_data: BaseModel):

    keys = item.__dict__.keys()
    for key in keys:
        if not str(key).startswith('_') and hasattr(new_item_data, key):
            new_value = getattr(new_item_data, key)
            setattr(item, key, new_value)

    db.commit()
    db.refresh(item)
    return item
