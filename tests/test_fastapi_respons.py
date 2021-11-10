from typing import List, Tuple, Type, Optional

import uvicorn
import fastapi
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic.fields import ModelField


class Item(BaseModel):
    id: int
    value: str


class Message(BaseModel):
    message: str


db_items: List[Item] = [
    Item(id=0, value='Zero'),
    Item(id=1, value='One'),
    Item(id=2, value='Two'),
    Item(id=3, value='Three')
]


read_item_responses = {
    404: {
        "model": Message,
        "description": "The item was not found"
    },
    200: {
        "description": "Item requested by ID",
        "content": {
            "application/json": {
                "example": {"id": 12, "value": "Twelve"}
            }
        },
    }
}


app = FastAPI()


@app.get(
    '/items/{item_id}',
    response_model=Item,
    responses=read_item_responses
)
async def read_item(item_id: int):
    try:
        return db_items[item_id]
    except IndexError as e:
        return JSONResponse(status_code=404, content={'message': 'Item not found'})


@app.post(
    '/items/',
    response_model=Item
)
async def add_item(value: str):
    new_item = Item(id=0, value=value)
    db_items.append(new_item)
    new_item_index = len(db_items) - 1
    # db_items[new_item_index].id = new_item_index
    new_item.id = new_item_index
    return new_item


def update_item_values(fields_dict: dict, old_values: Item, new_raw_values: dict):
    # item_type: dict = kwargs['item_model']
    # if item_type is dict:
    #     print(item_type)
    #     pass
    # return tuple(kwargs.values())
    fields_keys = fields_dict.keys()
    new_value_keys = new_raw_values.keys()
    for key in fields_keys:
        if key not in new_value_keys:
            old_value = old_values.__getattribute__(key)
            new_raw_values[key] = old_value

    return new_raw_values


if __name__ == '__main__':
    # print(update_item_values.__annotations__)
    # kwargs_model = {
    #     'hello': int,
    #     'bye': str,
    #     'item_model': dict,
    #     'return': Tuple[int, str, str]
    # }
    # update_item_values.__annotations__.update(**kwargs_model)
    #
    # kwargs = {
    #     'hello': 1,
    #     'bye': 'string1',
    #     'item_model': Item.__fields__
    # }
    # print(update_item_values(**kwargs))
    old_item = Item(id=1, value='value')
    new_item_data = {
        'value': 'One'
    }

    full_new_item_data: dict = update_item_values(Item.__fields__, old_item, new_item_data)
    old_item = Item(**full_new_item_data)
    print(old_item)

    variable1: Optional[int] = 1
    variable2: int = 2

    var_type1 = type(Optional[int])
    var_type2 = type(int)

    print(var_type1.__dict__, var_type2.__dict__, sep='\n')

    #print(fun1(**args))

    # uvicorn.run("test_fastapi_respons:app", port=5001, reload=True, access_log=False)