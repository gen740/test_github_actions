from pytest import mark
import sys
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from tempfile_pool import NamedTemporaryFilePool

logfile = "log.txt"


@mark.parametrize("i", range(1000))
def test_case(i):
    with NamedTemporaryFilePool() as pool:
        print(f"Test case {i} started {pool.name}", file=sys.stderr)
        with open(logfile, "a") as f:
            f.write(f"Test case {i} started {pool.name}\n")

        engine = create_engine(f"sqlite:///{pool.name}")

        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String)

        # テーブル作成
        Base.metadata.create_all(engine)

        # セッション作成
        Session = sessionmaker(bind=engine)
        session = Session()

        # データ書き込み
        user = User(name="alice")
        session.add(user)
        session.commit()

        # セッションと接続を明示的にクローズ
        # session.close()
        # engine.dispose()
