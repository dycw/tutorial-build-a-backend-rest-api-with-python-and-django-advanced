from app.calc import add


def test_main() -> None:
    assert add(1, 2) == 4
