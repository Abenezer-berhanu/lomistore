import pytest

from orders.phone import normalize_phone


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("0911223344", "+251911223344"),
        ("0711223344", "+251711223344"),
        ("911223344", "+251911223344"),
        ("251911223344", "+251911223344"),
        ("+251 91 122 3344", "+251911223344"),
        ("(091) 122-3344", "+251911223344"),
        ("+14155550123", "+14155550123"),
    ],
)
def test_valid_phones(raw: str, expected: str) -> None:
    assert normalize_phone(raw) == expected


@pytest.mark.parametrize("raw", ["", "hello", "0811223344", "09112233", "091122334455", "+0123"])
def test_invalid_phones(raw: str) -> None:
    assert normalize_phone(raw) is None
