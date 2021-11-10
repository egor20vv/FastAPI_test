import re

from typing import Optional, List, Generator, Tuple

from pydantic import BaseModel, validator, ValidationError
from pydantic.error_wrappers import ErrorWrapper


class MultiExceptionsHandler(list):
    def __init__(self):
        super(MultiExceptionsHandler, self).__init__(())

    def append(self, exc: str):
        return super(MultiExceptionsHandler, self).append(exc)

    def try_raise(self) -> None:
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
        errors: List[ErrorWrapper] = exception.args[0]
        info = []
        for error in errors:
            loc: str = list(error.loc_tuple())[0]
            exc: Tuple[str] = error.exc
            info.append((loc, exc))
        return info


# -- Message classes --
class BaseMessage(BaseModel):
    sender_id: int
    receiver_id: int
    text: str


class MessageCreate(BaseMessage):

    @validator('sender_id')
    def check_sender_existence(cls, sender_id: int):
        return sender_id

    @validator('receiver_id')
    def check_receiver_existence(cls, receiver_id: int):
        return receiver_id

    @validator('text')
    def check_text_message(cls, text: str):
        return text


class __MessageGet:
    status: int


class MessageEdit(MessageCreate, __MessageGet):
    @validator('status', check_fields=False)
    def check_status(cls, status: int):
        return status


class Message(BaseMessage, __MessageGet):
    id: int

    # receiver: User
    # sender: User

    class Config:
        orm_mode = True


# -- User classes --
class BaseUser(BaseModel):
    nik_name: str
    fst_name: Optional[str] = None
    sec_name: Optional[str] = None


class UserCreate(BaseUser):
    # @multi_error_validating('nik_name')
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


class __UserGet(BaseModel):
    status: int


class UserEdit(__UserGet, UserCreate):
    @validator('status')
    def check_status_is_correct(cls, status: int):
        with MultiExceptionsHandler() as exc:
            if status not in (0, 1):
                exc += f'value \'{status}\' must be in range (0, 1)'

        return status


class User(BaseUser, __UserGet):
    id: int

    received_messages: List[Message] = []
    sent_messages: List[Message] = []

    class Config:
        orm_mode = True


# try:
#     new_user_data = {
#         'nik_name': "egor20vv",
#         'aaa': 'some data'
#     }
#     new_user = UserCreate(**new_user_data)
#     pass
# except ValidationError as e:
#     print(e)
#     info = MultiExceptionsHandler.get_exception_info(e)
#     print('dict repr:', info)
#     pass
