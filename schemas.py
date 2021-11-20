import re
from typing import List, Tuple

from MetaBaseModel.main import InteractionKinds as IK, meta_constructor, meta_validator, MetaSchemaFactory, SchemaField

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


class Message(metaclass=MetaSchemaFactory):
    # --------
    #  Fields
    # --------
    id = SchemaField(int, IK.GET)
    sender_id = SchemaField(int, IK.CREATE | IK.GET)
    receiver_id = SchemaField(int, IK.CREATE | IK.GET)
    text = SchemaField(str, IK.ALL)
    status = SchemaField(int, IK.GET | IK.EDIT, default=0)

    # --------------
    #  Constructors
    # --------------
    @classmethod
    @meta_constructor(IK.CREATE)
    def init_create(cls, sender_id: int, receiver_id: int, text: str):
        return None

    @classmethod
    @meta_constructor(IK.EDIT)
    def init_edit(cls, text: str, status: int = 0):
        return None

    @classmethod
    @meta_constructor(IK.GET)
    def init_edit(cls, id: int, sender_id: int, receiver_id: int, text: str, status: int = 0):
        return None

    # ------------
    #  Validators
    # ------------
    @meta_validator('text')
    def check_text_message(cls, text: str):
        return text

    @meta_validator('status')
    def check_status(cls, status: int):
        return status


class User(metaclass=MetaSchemaFactory):
    """
    Fields::

        :id integer
        :nik_name acceptable len is [2, 32); accepted letters is [_a-zA-z0-9] + '@' as a first symbol
        :fst_name acceptable len is [2, 16]
        :sec_name acceptable len is [2, 16]
        :status acceptable values [0, 1]
        :received_messages List[Message], default is [],
        :sent_messages List[Message], default is [],
    """

    # --------
    #  Fields
    # --------
    id = SchemaField(int, IK.GET)
    nik_name = SchemaField(str, IK.ALL)
    fst_name = SchemaField(str, IK.ALL)
    sec_name = SchemaField(str, IK.ALL)
    status = SchemaField(int, IK.GET | IK.EDIT, default=0)

    received_messages = SchemaField(List[Message.Get], IK.GET)
    sent_messages = SchemaField(List[Message.Get], IK.GET)

    # --------------
    #  Constructors
    # --------------
    @classmethod
    @meta_constructor(IK.CREATE)
    def init_create(cls, nik_name: str, fst_name: str, sec_name: str):
        return None

    @classmethod
    @meta_constructor(IK.EDIT)
    def init_edit(cls, nik_name: str, fst_name: str, sec_name: str, status: int = 0):
        return None

    @classmethod
    @meta_constructor(IK.GET)
    def init_edit(cls, id: int, nik_name: str, fst_name: str, sec_name: str,
                  received_messages: List[Message.Get], sent_messages: List[Message.Get], status: int = 0):
        return None

    # ------------
    #  Validators
    # ------------
    @meta_validator('nik_name')
    def check_nik_name(cls, nik_name: str):
        if nik_name.startswith('@'):
            nik_name = nik_name.replace('@', '')
        with MultiExceptionsHandler() as exc:
            if len(nik_name) < 2:
                exc += f'value \'{nik_name}\' is too short'
            if len(nik_name) >= 32:
                exc += f'value \'{nik_name}\' is too large'
            if not re.match(r'^[\w_]+$', nik_name):
                exc += f'value \'{nik_name}\' has a wrong format: acceptable chars is (_a-zA-z0-9)'

        return '@' + nik_name

    @meta_validator('fst_name')
    def check_fst_name(cls, fst_name: str):
        with MultiExceptionsHandler() as exc:
            if len(fst_name) < 2:
                exc += f'value \'{fst_name}\' is too short'
            if len(fst_name) > 16:
                exc += f'value \'{fst_name}\' is too large'

        return fst_name

    @meta_validator('sec_name')
    def check_sec_name(cls, sec_name: str):
        with MultiExceptionsHandler() as exc:
            if len(sec_name) < 2:
                exc += f'value \'{sec_name}\' is too short'
            if len(sec_name) > 16:
                exc += f'value \'{sec_name}\' is too large'

        return sec_name

    @meta_validator('status')
    def check_status_is_correct(cls, status: int):
        with MultiExceptionsHandler() as exc:
            if status not in (0, 1):
                exc += f'value \'{status}\' must be in range (0, 1)'

        return status
