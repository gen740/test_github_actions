from pytest import mark
from tempfile_pool import NamedTemporaryFilePool

logfile = "log.txt"


@mark.parametrize("i", range(10000))
def test_case(i):
    with NamedTemporaryFilePool() as pool:
        with open(logfile, "a") as f:
            f.write(f"Test case {i} started {pool.name}\n")
