from os import getenv
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = f'postgresql://{getenv("POSTGRES_USER")}:{getenv("POSTGRES_PASSWORD")}@postgres/{getenv("POSTGRES_DB")}'

engine = create_engine(DATABASE_URL)
SessionLocaL = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class ReprBase:
    def __repr__(self) -> str:
        excl = ("_sa_adapter", "_sa_instance_state")
        values = {k: v for k, v in vars(self).items() if not k.startswith("_") and not any(hasattr(v, a) for a in excl)}
        values_str = ", ".join(f"{k}={v!r}" for k, v in sorted(values.items()))
        return f"{self.__class__.__name__}({values_str})"


Base = declarative_base(cls=ReprBase)


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocaL()
    try:
        yield db
    finally:
        db.close()
