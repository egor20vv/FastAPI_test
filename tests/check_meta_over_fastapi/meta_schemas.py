from tests.check_meta_over_fastapi.MetaBaseModel.main import MetaSchemaFactory, SchemaField, InteractionKinds as IK, \
    meta_validator, meta_constructor


class BaseSchema(metaclass=MetaSchemaFactory):
    id = SchemaField(int, IK.GETABLE)
    name = SchemaField(str, IK.GETABLE | IK.EDITABLE | IK.CREATABLE)
    password = SchemaField(str, IK.CREATABLE)
    status = SchemaField(int, IK.EDITABLE | IK.GETABLE, 0)

    @meta_validator('status')
    def check_status(cls, status):
        if status not in range(4):
            raise ValueError(f'status must be in range [0;4), but now is {status}')
        else:
            return status

    @classmethod
    @meta_constructor(IK.CREATABLE)
    def init_create(cls, name: str, password: str, **kwargs):
        return None

    @classmethod
    @meta_constructor(IK.GETABLE)
    def init_get(cls, id: int, name: str, status: int = 0, **kwargs):
        return None

    @classmethod
    @meta_constructor(IK.EDITABLE)
    def init_edit(cls, name: str, status: int = 0, **kwargs):
        return None


class BaseSchema1(metaclass=MetaSchemaFactory):
    pass


def check_constructors(user_data: dict):
    print("check constructors:")

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
    print("check cross schemas constructing")

    # raises error "id field required":
    # edit = BaseSchema.Edit(**user_data)
    # get = BaseSchema.Get(edit)

    # works!
    get = BaseSchema.Get(**user_data)
    edit = BaseSchema.Edit(get)

    print(get.dict())
    print(edit.dict())


def check_validators(user_data: dict):
    edit1 = BaseSchema.init_edit('Egor', 1)
    # raises error:
    # edit2 = BaseSchema.init_edit('Sonya', 10)


def main():
    user_data = {
        'id': 1,
        'name': 'Egor',
        'password': 'password',
        'status': 3
    }

    check_constructors(user_data)
    check_cross_schemas_constructing(user_data)
    check_validators(user_data)

    return


if __name__ == '__main__':
    main()

