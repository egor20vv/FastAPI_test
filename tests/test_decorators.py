def multiply_value(factor: float):
    def decorator(fun):
        print(factor * fun(5))

    return decorator


def add_value(fun):
    def wrapper(*args, **kwargs):
        return 10 + fun(*args, **kwargs)
    return wrapper


@multiply_value(4)
@add_value
def my_fun(val: int):
    return val


