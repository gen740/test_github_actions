from pytest import mark
import sys
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from tempfile_pool import NamedTemporaryFilePool

logfile = "log.txt"

# 終了まで参照を保持してGC/クローズを避ける
_leaked = []


@mark.parametrize("i", range(1000))
def test_case(i):
    with NamedTemporaryFilePool() as pool:
        print(f"Test case {i} started {pool.name}", file=sys.stderr)
        with open(logfile, "a") as f:
            f.write(f"Test case {i} started {pool.name}\n")

        engine = create_engine(f"sqlite:///{pool.name}")

        # ここでファイルを掴む接続を明示的に作り、閉じずに保持する（Windowsで削除失敗しやすくなる）
        conn = engine.connect()
        _leaked.append(conn)
        _leaked.append(engine)

        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String)

        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()
        _leaked.append(session)

        user = User(name="alice")
        session.add(user)
        session.commit()

        if i % 100 == 0:
            assert False, f"Intentional failure at iteration {i}"
