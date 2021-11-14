from typing import Dict, Tuple, Union
from typing import Any

from pydantic import BaseModel, BaseConfig
from pydantic.fields import ModelField


class CallStaticInit:

    @staticmethod
    def _add_fields(meta_model: Dict[str, Union[Any, Tuple[Any, Any]]]):
        def decorator(meta_cls):

            type_meta_model = {}
            for key, val in meta_model.items():
                _type: None
                if val.__class__ is Tuple[Any, Any]:
                    _type, _val = val
                    if _val.__class__ is _type:
                        setattr(meta_cls, key, _val)
                    else:
                        raise ValueError(f'meta_model["{key}"] has wrong item (Tuple[val_type, value]): '
                                         f'the value "{_val}" has other type differs to the val_type "{_type}"')
                else:
                    _type = val

                if _type.__class__ is not type:
                    raise ValueError(f'meta_model["{key}"] has wrong item: {_type} is not a type')

                type_meta_model.__setitem__(key, _type)

            if hasattr(meta_cls, '__annotations__'):
                old_annotations = meta_cls.__annotations__
                type_meta_model.update(old_annotations)
            meta_cls.__annotations__ = type_meta_model

            return meta_cls

        return decorator

    @staticmethod
    def _args_to_kwargs(_args: Tuple[Tuple[Any], Dict[str, Any]], _model: Dict[str, Any]) -> Dict[str, Any]:
        loc_args, loc_kwargs = _args
        is_kwargs = len(loc_kwargs) > 0
        is_args = len(loc_args) > 0
        loc_args_index: int = 0

        result: Dict[str, Any] = {}
        for key, type_ in _model.items():
            if is_kwargs and key in loc_kwargs.keys():
                loc_kwargs_val = loc_kwargs[key]
                if loc_kwargs_val.__class__ is type_:
                    result[key] = loc_kwargs_val
                else:
                    TypeError('Some error')
            elif is_args and loc_args[loc_args_index].__class__ is type_:
                result[key] = loc_args[loc_args_index]
                loc_args_index += 1
            else:
                ValueError(f'filed required {key}')
        return result

    def __new__(cls, *args, **kwargs):
        external = type(*args)

        _create_model = {
            'name': str,
            'status': int
        }

        @cls._add_fields(_create_model)
        class Create(BaseModel):
            def __init__(self, *args, **kwargs):
                data = cls._args_to_kwargs((args, kwargs), _create_model)
                super().__init__(**data)

            class Config:
                extra = 'allow'

        external.Create = Create

        return external


class BaseSchema(metaclass=CallStaticInit):
    pass


class BaseSchema1(metaclass=CallStaticInit):
    pass


my_create = BaseSchema.Create('Egor', 4)
print(my_create.dict())

create1 = BaseSchema.Create
create2 = BaseSchema1.Create
print(id(create1) == id(create2))
