# test.py
def test_print_captured():
    print("this should NOT be shown when test passes")
    assert 1 + 1 == 2


def test_print_on_failure():
    print("this should be shown when test fails")
    assert 1 + 1 == 3
