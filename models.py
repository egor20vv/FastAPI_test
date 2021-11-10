from sqlalchemy import Column, ForeignKey, Integer, Text, BLOB, NVARCHAR, VARCHAR, Boolean
from sqlalchemy.orm import relationship

from database import Base


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    text = Column(NVARCHAR(256), nullable=False)
    status = Column(Integer, nullable=False, default=0)

    receiver = relationship('User', back_populates='received_messages', foreign_keys='Message.receiver_id')
    sender = relationship('User', back_populates='sent_messages', foreign_keys='Message.sender_id')


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True, index=True)
    nik_name = Column(VARCHAR(length=32), nullable=False, unique=True, index=True)
    fst_name = Column(NVARCHAR(length=16), nullable=True, default='')
    sec_name = Column(NVARCHAR(length=16), nullable=True, default='')
    status = Column(Integer, nullable=False, default=0)

    received_messages = relationship('Message', back_populates='receiver', foreign_keys='Message.receiver_id')
    sent_messages = relationship('Message', back_populates='sender', foreign_keys='Message.sender_id')



