from typing import Tuple, Any, Dict, Iterable

from pydantic import validator, create_model, BaseModel


class ValidatorWrapper:
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


def args_to_kwargs(_args: Tuple[Any], _kwargs: Dict[str, Any], _model_names: Iterable[str]) -> Dict[str, Any]:
    data = _kwargs.copy()

    arg_name = iter(_model_names)
    for arg_val in _args:
        name = next(arg_name, None)
        if name is None:
            break
        data[name] = arg_val

    return data


def check_model(meta_model: Dict[str, Tuple]):
    for key, val in meta_model.items():
        if len(val) == 2:
            type_, default_ = val
            if default_.__class__ is not type_:
                raise ValueError(f'meta_model["{key}"] has wrong item (Tuple[val_type, value]): '
                                 f'the value "{default_}" has other type differs to the val_type "{type_}"')
        elif len(val) != 1:
            raise ValueError(f'meta_model["{key}"] has wrong tuple value "{val}": '
                             f'accepted (Tuple[<field_type>,<default_value>] or Tuple[<field_type>]) ')

    return None


def create_base_model_class(model_name: str,
                            _model: Dict[str, Tuple],
                            validator_wrappers: Iterable[ValidatorWrapper]) -> Any:
    check_model(_model)

    fields = {}
    for key, attr in _model.items():
        if len(attr) == 1:
            fields[key] = (attr[0], ...)
        elif len(attr) == 2:
            fields[key] = attr

    validators = {}
    for valid in validator_wrappers:
        validators[valid.get_fun_name()] = validator(valid.get_field_name(),
                                                     check_fields=False,
                                                     allow_reuse=True)(valid.get_fun())

    class LocBaseModel(BaseModel):

        def __init__(self, *args, **kwargs):
            if args != () and issubclass(args[0].__class__, BaseModel):
                super().__init__(**args[0].dict())
            else:
                data = args_to_kwargs(args, kwargs, _model.keys())
                super().__init__(**data)

        class Config:
            orm_mode = True

    basis_model = create_model(model_name,
                               __base__=LocBaseModel,
                               __validators__=validators,
                               **fields)
    return basis_model
