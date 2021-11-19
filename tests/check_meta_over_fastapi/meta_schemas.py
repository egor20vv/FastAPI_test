from pydantic import BaseModel, create_model

from tests.check_meta_over_fastapi.meta_tests import MetaSchemaFactory, SchemaField
from tests.check_meta_over_fastapi.meta_tests import InteractionKinds as IK


class BaseSchema(metaclass=MetaSchemaFactory):
    id = SchemaField(int, IK.GETABLE)
    name = SchemaField(str, IK.GETABLE | IK.EDITABLE | IK.CREATABLE)
    password = SchemaField(str, IK.CREATABLE)
    status = SchemaField(int, IK.EDITABLE | IK.GETABLE, 0)

    @classmethod
    @MetaSchemaFactory.constructor_interface(IK.CREATABLE)
    def init_create(cls, name: str, password: str, **kwargs):
        return None

    @classmethod
    @MetaSchemaFactory.constructor_interface(IK.GETABLE)
    def init_get(cls, id: int, name: str, status: int, **kwargs):
        return None

    @classmethod
    @MetaSchemaFactory.constructor_interface(IK.EDITABLE)
    def init_edit(cls, name: str, status: int, **kwargs):
        return None


class BaseSchema1(metaclass=MetaSchemaFactory):
    pass


def check_constructors(user_data: dict):
    kwargs_to_manual_init = BaseSchema.init_create(**user_data)
    print(kwargs_to_manual_init.dict())

    other_to_init = BaseSchema.Create(kwargs_to_manual_init)
    print(other_to_init.dict())

    args_to_init = BaseSchema.Create('Egor', 'password')
    print(args_to_init.dict())

    kwargs_to_init = BaseSchema.Create(**user_data)
    print(kwargs_to_init.dict())

    # Here is error occurs:
    # not_enough_args = BaseSchema.Create('Egor')
    # print(not_enough_args.dict())


def check_cross_schemas_constructing(user_data: dict):
    # raises error "id field required":
    # edit = BaseSchema.Edit(**user_data)
    # get = BaseSchema.Get(edit)

    # works!
    get = BaseSchema.Get(**user_data)
    edit = BaseSchema.Edit(get)

    print(get.dict())
    print(edit.dict())


def main():
    user_data = {
        'id': 1,
        'name': 'Egor',
        'password': 'password',
        'status': 10
    }

    # check_constructors(user_data)
    # check_cross_schemas_constructing(user_data)

    return


if __name__ == '__main__':
    main()

