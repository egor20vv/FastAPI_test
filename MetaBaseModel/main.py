from enum import IntFlag, auto
from typing import Dict, Tuple
from typing import Any

from pydantic import BaseModel

from . import private


class InteractionKinds(IntFlag):
    CREATE = auto()
    EDIT = auto()
    GET = auto()
    ALL = CREATE | EDIT | GET


class SchemaField:
    """
    Use it to note a field of base model meta classes

    Example::

        IK = InteractionKinds
        class User(metaclass=MetaSchemaFactory):
            id = SchemaField(int, IK.EDIT, 0)
            messages = SchemaField(List[str], IK.EDIT | IK.CREATE)
    """

    class Default:
        pass

    def __init__(self, type_, interaction_kinds: int = InteractionKinds.ALL, default: Any = Default):
        if type_.__class__ is not type and (not hasattr(type_, '__origin__') or type_.__origin__.__class__ is not type):
            raise ValueError('type_ is not a type')

        if default is not self.Default and default.__class__ is not type_:
            raise TypeError(f'default value "{default}" has differ type to the type_ "{type_}"')

        self._type = type_
        self._inter = interaction_kinds
        self._default = default

    def get(self) -> Tuple[Any, int, Any]:
        return self._type, self._inter, self._default


def meta_constructor(type_of_interaction: InteractionKinds):
    """
    decorator to note constructor to any of created metaclasses (Create|Edit|Get)

    Example::

        IK = InteractionKinds

        class User(metaclass=MetaSchemaFactory):

            id = SchemaField(int, IK.GET)
            name = SchemaField(str, IK.ALL, 'some_default_name')
            email = SchemaField(str, IK.ALL)
            password = SchemaField(str, IK.CREATE)

            @classmethod # or @staticmethod
            @meta_constructor(IK.CREATE)
            def init_create(cls, email: str, password: str, name: str = 'default_name'):
                return None

    :param type_of_interaction: use only one of InteractionKinds except (InteractionKinds.ALL)
    """

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

            if type_of_interaction is InteractionKinds.GET and hasattr(wrapper_cls, 'Get'):
                return wrapper_cls.Get(**data)
            elif type_of_interaction is InteractionKinds.EDIT and hasattr(wrapper_cls, 'Edit'):
                return wrapper_cls.Edit(**data)
            elif type_of_interaction is InteractionKinds.CREATE and hasattr(wrapper_cls, 'Create'):
                return wrapper_cls.Create(**data)
            else:
                raise ValueError(f'Wrong InteractionKinds value ({type_of_interaction})')

        return wrapper

    return decorator


def meta_validator(filed_name: str):
    """
    decorate function makes of it validator in created metaclasses

    Example::

        class User(metaclass=MetaSchemaFactory):

            status = SchemaField(int, IK.ALL)

            @meta_validator('status')
            def check_status_is_correct(cls, status: int): # cls is must to be
                if status not in (0, 1, 2):
                    raise ValueError(f'value \'{status}\' must be in range (0, 1, 2)'
                else:
                    return status

        return status


    :param filed_name:
    :return:
    """

    def decorator(fun):
        return private.ValidatorWrapper(fun, filed_name)
    return decorator


class MetaSchemaFactory:
    """
    Creates 3 sub-classes: Create, Edit, Get. Each of them inherits from BaseModel.

    Example::

        IK = InteractionKinds

        class User(metaclass=MetaSchemaFactory):

            id = SchemaField(int, IK.GET)
            status = SchemaField(int, IK.ALL, 0) # in range [0;2]

            @classmethod
            @meta_constructor(IK.GET)
            def init_edit(cls, id: int, status: int = 0)
                return None

            @meta_validator('status')
            def check_status_is_correct(cls, status: int): # cls is must to be
                if status not in (0, 1, 2):
                    raise ValueError(f'value \'{status}\' must be in range (0, 1, 2)'
                else:
                    return status

        get_user = User.Get(id=2) # equal to User.Get(id=2, status=0)
        # get_user: {'id': 2, 'status': 0}

        create_user = User.Create(get_user)
        # create_user: {'status': 0}




    """

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

        external.Create = private.create_base_model_class(args[0] + '_Create', _create_model, validators)
        external.Edit = private.create_base_model_class(args[0] + '_Edit', _edit_model, validators)
        external.Get = private.create_base_model_class(args[0] + '_Get', _get_model, validators)

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

                if InteractionKinds.GET in inter:
                    _get_model[key] = model_value
                if InteractionKinds.CREATE in inter:
                    _create_model[key] = model_value
                if InteractionKinds.EDIT in inter:
                    _edit_model[key] = model_value
        return
