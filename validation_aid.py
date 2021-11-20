from typing import List, Tuple
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper


class MultiExceptionsHandler(list):
    """
    Inherits from the builtins list but takes strings only to convert them to error \n
    Class is a context manager (allows WITH construction) \n
    Example: \n
    with MultiExceptionsHandler() as exc:
        if True:
            exc += 'some exception message'
        if True:
            exc += 'some other exception message'
        if False:
            exc += 'another exception'

    # Raised error: ValueError('some exception message', 'some other exception message')
    """

    def __init__(self):
        super(MultiExceptionsHandler, self).__init__(())

    def append(self, exc: str):
        return super(MultiExceptionsHandler, self).append(exc)

    def try_raise(self) -> None:
        """
        Tries to raise exception if some was appended \n

        Note: Method is relevant if you use it class as not as context manager

        :return: None
        """
        if len(self) != 0:
            raise ValueError(*self)
        return None

    def __iadd__(self, other):
        if type(other) is not str:
            raise TypeError("value is not a string")
        self.append(other)
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.try_raise()

    @staticmethod
    def get_exception_info(exception: Exception) -> List[Tuple[str, Tuple[str]]]:
        if exception.__class__ is ValueError:
            return ValidationError(exception).errors()

        errors: List[ErrorWrapper] = exception.args[0]
        info = []
        for error in errors:
            loc: str = list(error.loc_tuple())[0]
            exc: Tuple[str] = error.exc
            info.append((loc, exc))
        return info
