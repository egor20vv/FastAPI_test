from enum import IntFlag, auto
from typing import Dict, Tuple, Iterable
from typing import Any

from pydantic import BaseModel, validator, create_model


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
    def validator(cls, filed_name: str):
        def decorator(fun):
            return cls._ValidatorWrapper(fun, filed_name)
        return decorator

    class _ValidatorWrapper:
        def get_fun(self):
            return self._fun

        def get_fun_name(self) -> str:
            return self._name

        def get_field_name(self) -> str:
            return self._field_name

        def __init__(self, fun, field_name: str):
            self._fun = fun
            self._name = fun.__name__
            self._field_name = field_name

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
            name = next(arg_name, None)
            if name is None:
                break
            data[name] = arg_val
        for i in _kwargs.keys():
            name = next(arg_name, None)
            if name is None:
                break
            data[name] = _kwargs[name]

        return data

    @classmethod
    def _create_base_model_class(cls,
                                 model_name: str,
                                 _model: Dict[str, Tuple],
                                 validator_wrappers: Iterable[_ValidatorWrapper]) -> Any:

        fields = {}
        for key, attr in _model.items():
            if len(attr) == 1:
                fields[key] = (attr[0], ...)
            elif len(attr) == 2:
                fields[key] = attr

        class LocalConfig:
            orm_mode = True

        validators = {}
        for valid in validator_wrappers:
            validators[valid.get_fun_name()] = validator(valid.get_field_name(),
                                                         check_fields=False,
                                                         allow_reuse=True)(valid.get_fun())

        basis_model = create_model(model_name, __config__=LocalConfig, __validators__=validators, **fields)

        class LocBaseModel(basis_model):

            def __init__(self, *args, **kwargs):
                if args != () and issubclass(args[0].__class__, BaseModel):
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

        validators = []
        # for func_name, func in args[2].items():
        #     if hasattr(func, '__dict__') and '__validator_config__' in func.__dict__.keys():
        #         validators[func_name] = func

        for func_name, func in args[2].items():
            if func.__class__ is cls._ValidatorWrapper:
                validators.append(func)

        _create_model = {}
        _edit_model = {}
        _get_model = {}

        cls._set_models(external, _create_model, _edit_model, _get_model)

        external.Create = cls._create_base_model_class('Create', _create_model, validators)
        external.Edit = cls._create_base_model_class('Edit', _edit_model, validators)
        external.Get = cls._create_base_model_class('Get', _get_model, validators)

        return external
