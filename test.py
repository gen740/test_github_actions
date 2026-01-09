from pytest import mark
import sys
from sqlalchemy import Column, Integer, String, create_engine, Engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import AbstractContextManager
from typing import Any, IO

from types import TracebackType
from tempfile_pool import NamedTemporaryFilePool

logfile = "log.txt"


class StorageSupplier(AbstractContextManager):
    def __init__(self, **kwargs: Any) -> None:
        self.tempfile: IO[Any] | None = None
        self.engine: Engine | None = None

    def __enter__(
        self,
    ) -> Engine:
        self.tempfile = NamedTemporaryFilePool().tempfile()
        self.engine = create_engine(f"sqlite:///{self.tempfile.name}")
        return self.engine

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.tempfile:
            self.tempfile.close()


@mark.parametrize("i", range(1000))
def test_case(i):
    with StorageSupplier() as engine:
        engine.connect()

        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String)

        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        user = User(name="alice")
        session.add(user)
        session.commit()
