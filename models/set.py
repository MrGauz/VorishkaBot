from enum import Enum

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from database import Base


class SetTypes(Enum):
    STATIC = 1
    ANIMATED = 2
    VIDEO = 3
    EMOJI = 4


class SetType(Base):
    __tablename__ = 'set_types'
    __table_args__ = {'mysql_collate': 'utf8mb4'}

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)


class Set(Base):
    __tablename__ = 'sets'
    __table_args__ = {'mysql_collate': 'utf8mb4'}

    id = Column(Integer, primary_key=True)
    set_type_id = Column(Integer, ForeignKey('set_types.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(256), nullable=False)
    title = Column(String(64), nullable=False)
    created_at_utc = Column(DateTime(timezone=True), server_default=func.now())

    set_type = relationship('SetType', backref='sets')
    user = relationship('User', backref='sets')
