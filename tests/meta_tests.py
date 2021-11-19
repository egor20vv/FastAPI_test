from enum import IntFlag, auto
from typing import Dict, Tuple, Union, Callable, List, Iterable
from typing import Any

from pydantic import BaseModel, BaseConfig, validator
from pydantic.fields import ModelField


class InteractionKinds(IntFlag):
    CREATABLE = auto()
    EDITABLE = auto()
    GETABLE = auto()


class SchemaField:

    class Default:
        pass

    def __init__(self, type_, inter: int, default: Any = Default):
        if type_.__class__ is not type:
            raise ValueError('type_ is not a type')

        if default is not self.Default and default.__class__ is not type_:
            raise TypeError(f'default value "{default}" has differ type to the type_ "{type_}"')

        self._type = type_
        self._inter = inter
        self._default = default

    def get(self) -> Tuple[Any, int, Any]:
        return self._type, self._inter, self._default


class MetaSchemaFactory:

    @classmethod
    def constructor_interface(cls, type_of_interaction: InteractionKinds):
        def decorator(fun):

            def wrapper(wrapper_cls, *args, **kwargs) -> BaseModel:
                code = fun.__code__
                arg_names = list(code.co_varnames)[:code.co_argcount]
                if arg_names[0] in ('self', 'cls'):
                    arg_names = arg_names[1:]

                    # if some attributes are missing or there are more of them than you need, reports an error
                    fun(None, *args, **kwargs)
                else:
                    # if some attributes are missing or there are more of them than you need, reports an error
                    fun(*args, **kwargs)

                data = cls._args_to_kwargs(args, kwargs, arg_names)

                if type_of_interaction is InteractionKinds.GETABLE and hasattr(wrapper_cls, 'Get'):
                    return wrapper_cls.Get(**data)
                elif type_of_interaction is InteractionKinds.EDITABLE and hasattr(wrapper_cls, 'Edit'):
                    return wrapper_cls.Edit(**data)
                elif type_of_interaction is InteractionKinds.CREATABLE and hasattr(wrapper_cls, 'Create'):
                    return wrapper_cls.Create(**data)
                else:
                    raise ValueError(f'Wrong InteractionKinds value ({type_of_interaction})')

            return wrapper

        return decorator

    @classmethod
    def _add_fields(cls, meta_model: Dict[str, Tuple]):
        def decorator(meta_cls):

            type_meta_model = {}
            for key, val in meta_model.items():
                _type: Any
                if len(val) == 2:
                    _type, _val = val
                    if _val.__class__ is _type:
                        setattr(meta_cls, key, _val)
                    else:
                        raise ValueError(f'meta_model["{key}"] has wrong item (Tuple[val_type, value]): '
                                         f'the value "{_val}" has other type differs to the val_type "{_type}"')
                elif len(val) == 1:
                    _type = val[0]
                else:
                    raise ValueError(f'meta_model["{key}"] has wrong tuple value: '
                                     f'accepted (Tuple[<field_type>,<default_value>] or Tuple[<field_type>]) ')

                if _type.__class__ is not type:
                    raise ValueError(f'meta_model["{key}"] has wrong item: {_type} is not a type')

                type_meta_model.__setitem__(key, _type)

            if hasattr(meta_cls, '__annotations__'):
                old_annotations = meta_cls.__annotations__
                type_meta_model.update(old_annotations)
            meta_cls.__annotations__ = type_meta_model

            return meta_cls

        return decorator

    @classmethod
    def _args_to_kwargs(cls, _args: Tuple[Any], _kwargs: Dict[str, Any], _model_names: Iterable[str]) -> Dict[str, Any]:
        data = {}

        arg_name = iter(_model_names)
        for arg_val in _args:
            data[next(arg_name)] = arg_val
        for i in _kwargs.keys():
            name = next(arg_name, None)
            if name is None:
                break
            data[name] = _kwargs[name]

        return data

    @classmethod
    def _create_base_model_class(cls, _model: Dict[str, Tuple]) -> Any:
        @cls._add_fields(_model)
        class LocBaseModel(BaseModel):

            class Config:
                extra = 'allow'

            def __init__(self, *args, **kwargs):
                if args != () and args[0].__class__ == LocBaseModel:
                    super().__init__(**args[0].dict())
                else:
                    data = cls._args_to_kwargs(args, kwargs, _model.keys())
                    super().__init__(**data)

        return LocBaseModel

    @classmethod
    def _set_models(cls,
                    external,
                    _create_model: Dict[str, Tuple],
                    _edit_model: Dict[str, Tuple],
                    _get_model: Dict[str, Tuple]):

        for key, val in external.__dict__.items():
            if val.__class__ is SchemaField:
                type_, inter, default = val.get()

                model_value = (type_,) if default is SchemaField.Default else (type_, default)

                if InteractionKinds.GETABLE in inter:
                    _get_model[key] = model_value
                if InteractionKinds.CREATABLE in inter:
                    _create_model[key] = model_value
                if InteractionKinds.EDITABLE in inter:
                    _edit_model[key] = model_value
        return

    def __new__(cls, *args, **kwargs):
        external = type(*args)

        _create_model = {}
        _edit_model = {}
        _get_model = {}

        cls._set_models(external, _create_model, _edit_model, _get_model)

        external.Create = cls._create_base_model_class(_create_model)
        external.Edit = cls._create_base_model_class(_edit_model)
        external.Get = cls._create_base_model_class(_get_model)

        return external


IK = InteractionKinds


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
    def init_get(cls, id_: int, name: str, status: int):
        return None

    @classmethod
    @MetaSchemaFactory.constructor_interface(IK.EDITABLE)
    def init_edit(cls, name: str, status: int):
        return None


class BaseSchema1(metaclass=MetaSchemaFactory):
    pass


user_data = {
    'id': 1,
    'name': 'Egor',
    'password': 'password',
    'status': 10
}


kwargs_to_manual_init = BaseSchema.init_create(**user_data)
print(kwargs_to_manual_init.dict())

other_to_init = BaseSchema.Create(kwargs_to_manual_init)
print(other_to_init.dict())

args_to_init = BaseSchema.Create('Egor', 'password')
print(args_to_init.dict())

kwargs_to_init = BaseSchema.Create(**user_data)
print(kwargs_to_init.dict())


create1 = BaseSchema.Create
create2 = BaseSchema1.Create
print(id(create1) == id(create2))
