import inspect
from typing import Union, Any


def does_raise_error(fun_or_str_or_none: Union[Any, str, None] = None):
    """
    Decorator gave a choice to user either
    (when in a decorated function some error occurs) raise an error or return None


    Decorator has 3 kinds of usage::

        # Use here default parameter name "raise_error"
        @does_raise_error
        # equal to @does_raise_error('raise_error')
        def fun_kind_1(raise_error: bool = True):
            pass

        # Same as first example
        @does_raise_error()
        def fun_kind_1(do_raise_error: bool = True):
            pass

        # You can specify you own name of the label
        @does_raise_error('do_raise_error')
        def fun_kind_1(do_raise_error: bool = True):
            pass

    You don't have to specify label ("raise_error" by default) in a decorated function::

        @does_raise_error
        def decorated_fun(**kwargs):
            raise ValueError('error occurs')

        >> decorated_fun(raise_error=False) == None
        Output: True


    :param fun_or_str_or_none: Is union to support multi mode
    """

    argument_name: str = 'raise_error'

    if fun_or_str_or_none.__class__ is str:
        argument_name = fun_or_str_or_none

    def decorator(fun):
        def wrapper(*args, **kwargs):
            var_names = list(fun.__code__.co_varnames)[:fun.__code__.co_argcount]
            kwargs_keys = kwargs.keys()

            raise_error_value: bool = True

            if argument_name in kwargs_keys:
                arg_name_of_kwargs = kwargs[argument_name]
                if arg_name_of_kwargs.__class__ is bool:
                    raise_error_value = arg_name_of_kwargs

            elif argument_name in var_names:
                argument_name_index = list(var_names).index(argument_name)
                if argument_name_index < len(args):
                    arg_name_of_args = args[argument_name_index]
                    if arg_name_of_args.__class__ is bool:
                        raise_error_value = arg_name_of_args
                else:
                    inspected_fun = inspect.signature(fun)
                    key, param = list(inspected_fun.parameters.items())[argument_name_index]
                    if key == argument_name and param.default is not inspect.Parameter.empty:
                        raise_error_value = param.default

            # Depends on the raise_error_value \
            # return value of the function, return None or raise an error from that function
            try:
                return fun(*args, **kwargs)
            except Exception as e:
                if raise_error_value:
                    raise e
                else:
                    print(e)
                    return None

        return wrapper

    if fun_or_str_or_none.__class__ is not str and fun_or_str_or_none is not None:
        return decorator(fun_or_str_or_none)
    else:
        return decorator
