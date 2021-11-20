from enum import IntFlag, auto
from typing import Dict, Tuple, Iterable
from typing import Any

from pydantic import BaseModel, validator, create_model

# from .private import args_to_kwargs, ValidatorWrapper
from . import private


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


def meta_constructor(type_of_interaction: InteractionKinds):
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

            data = private.args_to_kwargs(args, kwargs, arg_names)

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


def meta_validator(filed_name: str):
    def decorator(fun):
        return private.ValidatorWrapper(fun, filed_name)
    return decorator


class MetaSchemaFactory:

    def __new__(cls, *args, **kwargs):
        external = type(*args)

        validators = []
        for func_name, func in args[2].items():
            if func.__class__ is private.ValidatorWrapper:
                validators.append(func)

        _create_model = {}
        _edit_model = {}
        _get_model = {}

        cls._set_models(external, _create_model, _edit_model, _get_model)

        external.Create = private.create_base_model_class('Create', _create_model, validators)
        external.Edit = private.create_base_model_class('Edit', _edit_model, validators)
        external.Get = private.create_base_model_class('Get', _get_model, validators)

        return external

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
