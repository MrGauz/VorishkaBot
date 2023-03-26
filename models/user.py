from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, func

from database import Base


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'mysql_collate': 'utf8mb4'}

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(32))
    first_name = Column(String(256), nullable=False)
    last_name = Column(String(256), default=None)
    language_code = Column(String(3), default=None)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
