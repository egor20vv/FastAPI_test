import re

from typing import Optional, List, Generator, Tuple

from pydantic import BaseModel, validator, ValidationError
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


# -- Message classes --
class BaseMessage(BaseModel):
    """
    Base of message table
    """
    sender_id: int
    receiver_id: int
    text: str

    @validator('sender_id')
    def check_sender_existence(cls, sender_id: int):
        return sender_id

    @validator('receiver_id')
    def check_receiver_existence(cls, receiver_id: int):
        return receiver_id

    @validator('text')
    def check_text_message(cls, text: str):
        return text


class MessageCreate(BaseMessage):
    """
    Has all necessary data to create Message \n
    Here is no data (fields) to return it to user directly (as like as password)
    """
    pass


class __MessageGet:
    """
    Intermediate class contains fields for MessageEdit and Message classes
    """
    status: int


class MessageEdit(MessageCreate, __MessageGet):
    """
    Contains editable fields
    """

    @validator('status', check_fields=False)
    def check_status(cls, status: int):
        return status


class Message(BaseMessage, __MessageGet):
    """
    Contains all data except data that cannot be returned
    (like the password that may be contained in the UserCreate class)
    """
    id: int

    # receiver: User
    # sender: User

    class Config:
        orm_mode = True


# -- User classes --
class BaseUser(BaseModel):
    """
    Base of user table

    :arg nik_name: acceptable len is [2, 32); accepted letters is [_a-zA-z0-9] + '@' as a first symbol
    :arg fst_name: acceptable len is [2, 16]
    :arg sec_name: acceptable len is [2, 16]
    """

    nik_name: str
    fst_name: Optional[str] = None
    sec_name: Optional[str] = None

    def __init__(self,
                 nik_name: str,
                 fst_name: Optional[str] = None,
                 sec_name: Optional[str] = None,
                 **other_data
                 ):
        data = {
            'nik_name': nik_name
        }
        if fst_name is not None:
            other_data['fst_name'] = fst_name
        if sec_name is not None:
            other_data['sec_name'] = sec_name
        super().__init__(**data, **other_data)

    @validator('nik_name')
    def check_nik_name(cls, nik_name: str):
        if nik_name.startswith('@'):
            nik_name = nik_name.replace('@', '')
        with MultiExceptionsHandler() as exc:
            if len(nik_name) < 2:
                exc += f'value \'{nik_name}\' is too short'
            if len(nik_name) >= 32:
                exc += f'value \'{nik_name}\' is too large'
            if not re.match(r'[_a-zA-z0-9]', nik_name):
                exc += f'value \'{nik_name}\' has a wrong format: acceptable chars is (_a-zA-z0-9)'

        return '@' + nik_name

    @validator('fst_name')
    def check_fst_name(cls, fst_name: str):
        with MultiExceptionsHandler() as exc:
            if len(fst_name) < 2:
                exc += f'value \'{fst_name}\' is too short'
            if len(fst_name) > 16:
                exc += f'value \'{fst_name}\' is too large'

        return fst_name

    @validator('sec_name')
    def check_sec_name(cls, sec_name: str):
        with MultiExceptionsHandler() as exc:
            if len(sec_name) < 2:
                exc += f'value \'{sec_name}\' is too short'
            if len(sec_name) > 16:
                exc += f'value \'{sec_name}\' is too large'

        return sec_name


class UserCreate(BaseUser):
    """
    Has all necessary data to create User \n
    Here is no data (fields) to return it to user directly (as like as password)

    :arg nik_name: acceptable len is [2, 32); accepted letters is [_a-zA-z0-9] + '@' as a first symbol
    :arg fst_name: acceptable len is [2, 16]
    :arg sec_name: acceptable len is [2, 16]
    """

    def __init__(self,
                 nik_name: str,
                 fst_name: Optional[str] = None,
                 sec_name: Optional[str] = None,
                 **other_data
                 ):
        super().__init__(nik_name, fst_name, sec_name, **other_data)


class _UserGet(BaseModel):
    """
    Intermediate class contains fields for UserEdit and User classes

    :arg status: acceptable values [0, 1]
    """

    status: int  # acceptable values is [0, 1]

    def __init__(self, status: int, **other_data):
        # self.status = status
        data = {
            'status': status
        }
        super().__init__(**data, **other_data)


class UserEdit(BaseUser, _UserGet):
    """
    Contains editable fields

    :arg nik_name: acceptable len is [2, 32); accepted letters is [_a-zA-z0-9] + '@' as a first symbol
    :arg fst_name: acceptable len is [2, 16]
    :arg sec_name: acceptable len is [2, 16]
    :arg status: acceptable values [0, 1]
    """

    def __init__(self,
                 nik_name: str,
                 status: int,
                 fst_name: Optional[str] = None,
                 sec_name: Optional[str] = None,
                 **other_data
                 ):
        data = {
            'status': status
        }

        super(UserEdit, self).__init__(nik_name, fst_name, sec_name, **data, **other_data)

        # super(_UserGet, self).__init__(status, **other_data)

    @validator('status', check_fields=False)
    def check_status_is_correct(cls, status: int):
        with MultiExceptionsHandler() as exc:
            if status not in (0, 1):
                exc += f'value \'{status}\' must be in range (0, 1)'

        return status


class User(BaseUser, _UserGet):
    """
    Contains all data except data that cannot be returned
    (like the password that may be contained in the UserCreate class)

    :arg id: integer
    :arg nik_name: acceptable len is [2, 32); accepted letters is [_a-zA-z0-9] + '@' as a first symbol
    :arg fst_name: acceptable len is [2, 16]
    :arg sec_name: acceptable len is [2, 16]
    :arg status: acceptable values [0, 1]
    :arg received_messages: List[Message], default is [],
    :arg sent_messages: List[Message], default is [],
    """
    id: int

    received_messages: List[Message] = []
    sent_messages: List[Message] = []

    def __init__(self,
                 _id: int,
                 nik_name: str,
                 status: int,
                 received_messages: List[Message] = None,
                 sent_messages: List[Message] = None,
                 fst_name: Optional[str] = None,
                 sec_name: Optional[str] = None,
                 **other_data):
        data = {
            'id': _id
        }
        if received_messages is not None:
            data['received_messages'] = received_messages
        if sent_messages is not None:
            data['sent_messages'] = sent_messages

        super().__init__(nik_name, fst_name, sec_name, **data, **other_data)

    class Config:
        orm_mode = True


# try:
#     new_user_data = {
#         'nik_name': "egor20vv",
#         'status': 0,
#         'fst_name': 'Egorka'
#     }
#     new_user = UserEdit(**new_user_data)
#     print(new_user.dict())
#     pass
# except ValidationError as e:
#     print(e)
#     info = MultiExceptionsHandler.get_exception_info(e)
#     print('dict repr:', info)
#     pass
