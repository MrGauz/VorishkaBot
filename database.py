from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Don't change the order of imports
from models.base import Base
from models.user import User  # noqa
from models.set import SetType, SetTypes  # noqa

from settings import DATABASE_ENGINE

engine = create_engine(DATABASE_ENGINE)
Session = sessionmaker(bind=engine)

# Create the tables in the database if they don't exist
Base.metadata.create_all(engine)


def user_exists(user_id: int) -> bool:
    session = Session()
    user = session.query(User).filter_by(user_id=user_id).first()
    session.close()
    return user is not None


def create_user(user_id: int, username: str, first_name: str = None, last_name: str = None,
                lang_code: str = None, is_premium: bool = False):
    session = Session()
    user = User(
        user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        language_code=lang_code,
        is_premium=is_premium
    )
    session.add(user)
    session.commit()
    session.close()


def get_all_users() -> list[User]:
    session = Session()
    users = session.query(User).all()
    session.close()
    return users


def seed_set_types() -> None:
    session = Session()
    session.add(SetType(name=SetTypes.STATIC.name))
    session.add(SetType(name=SetTypes.ANIMATED.name))
    session.add(SetType(name=SetTypes.VIDEO.name))
    session.add(SetType(name=SetTypes.EMOJI.name))
    session.commit()
    session.close()


seed_set_types()
