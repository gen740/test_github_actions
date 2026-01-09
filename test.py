from __future__ import annotations

from contextlib import AbstractContextManager
from types import TracebackType
from typing import Any, IO, Optional

from pytest import mark
from sqlalchemy import Column, Engine, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, scoped_session, sessionmaker
from sqlalchemy.orm.scoping import scoped_session as ScopedSessionType

from tempfile_pool import NamedTemporaryFilePool


class StorageSupplier(AbstractContextManager[Session]):
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.tempfile: Optional[IO[Any]] = None
        self.engine: Optional[Engine] = None
        self.scoped: Optional[ScopedSessionType] = None

    def __enter__(self) -> Session:
        # tempfile を確保
        self.tempfile = NamedTemporaryFilePool().tempfile()

        # Engine を作成
        self.engine = create_engine(f"sqlite:///{self.tempfile.name}")

        # scoped_session を作成し、Session インスタンスを返す
        factory = sessionmaker(bind=self.engine)
        self.scoped = scoped_session(factory)
        return self.scoped()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        # 要件: scoped_session / Session を閉じない（remove/closeしない）
        # ただし Engine と tempfile はこの CM の責務として処理する
        if self.engine is not None:
            self.engine.dispose()
        if self.tempfile is not None:
            self.tempfile.close()


_leaked_session: list[Session] = []


@mark.parametrize("i", range(100))
def test_case(i: int) -> None:
    with StorageSupplier() as session:
        # Session から Engine を取得（Session を返す設計なので engine 変数は存在しない）
        engine = session.get_bind()

        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String)

        Base.metadata.create_all(engine)

        user = User(name="alice")
        session.add(user)
        session.commit()

        # Session を意図的にリークさせる（削除時の挙動検証などに使う）
        _leaked_session.append(session)

        assert False, "Intentional Failure for Testing"
