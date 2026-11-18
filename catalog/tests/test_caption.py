"""Tests for catalog.caption.

Run them with:  pytest -v
"""

import pytest

from catalog.caption import (
    CaptionError,
    ParsedProduct,
    parse_caption,
    parse_price,
    parse_sizes,
)


# LEARN: a fixture is a reusable piece of test data or setup. Any test that
#   has a parameter with the same name (`full_caption`) receives its value.
# SENIOR: shared data lives in one place, so changing the example caption
#   doesn't mean editing ten tests.
# BEGINNER: copy the same caption string into every test.
# WHY NOT: copies drift apart, and a small change means editing many places.
@pytest.fixture
def full_caption() -> str:
    return (
        "Nike Air Force 1 White\n"
        "Price: 3,500 ETB\n"
        "Sizes: 40, 41, 42-44\n"
        "Original, made in Vietnam\n"
        "SOLD OUT\n"
    )


# SENIOR: test names say what behaviour is expected, so a failing test name
#   alone tells you what broke. `-> None` because tests return nothing.
def test_reads_every_part_of_a_full_caption(full_caption: str) -> None:
    # SENIOR: compare against one whole expected object. If anything is
    #   wrong, pytest prints a diff showing exactly which field differs.
    # BEGINNER: five separate asserts, one per field.
    # WHY NOT: the first failing assert stops the test, so you only learn
    #   about one wrong field at a time.
    assert parse_caption(full_caption) == ParsedProduct(
        name="Nike Air Force 1 White",
        price=3500,
        sizes=(40, 41, 42, 43, 44),
        description="Original, made in Vietnam",
        sold_out=True,
    )


def test_minimal_caption_uses_defaults() -> None:
    product = parse_caption("Puma Suede\nPrice: 2900\nSize: 41")

    assert product.description == ""
    # LEARN: `is False` checks for the real False. `== False` would also
    #   accept 0, which hides bugs.
    assert product.sold_out is False


# LEARN: parametrize runs the same test once per tuple.
#   pytest shows each one as a separate test: test_price_formats[3,500 ETB-3500]
# SENIOR: one test function covers many inputs, and adding a case is one line.
# BEGINNER: one test function per input (test_price_with_comma, ...).
# WHY NOT: lots of repeated code that only differs by the input.
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("3500", 3500),
        ("3,500 ETB", 3500),
        ("3500 birr", 3500),
        ("Br 2,800", 2800),
        (" 1,250.00 ", 1250),
    ],
)
def test_price_formats(text: str, expected: int) -> None:
    assert parse_price(text) == expected


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("free", "Can't read price"),
        ("0 ETB", "more than 0"),
    ],
)
def test_bad_price_raises(text: str, message: str) -> None:
    # LEARN: pytest.raises passes only if the code inside raises that error.
    #   `match` checks the message too (it's a regex search).
    # SENIOR: always check the message, not just the error type. Otherwise the
    #   test still passes when the code fails for a different reason.
    with pytest.raises(CaptionError, match=message):
        parse_price(text)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("40, 41, 42", (40, 41, 42)),
        ("40 41 42", (40, 41, 42)),
        ("42, 40, 42", (40, 42)),
        ("39-42", (39, 40, 41, 42)),
        ("38, 40-41", (38, 40, 41)),
        ("40, 41,", (40, 41)),
        ("41-41", (41,)),
    ],
)
def test_size_formats(text: str, expected: tuple[int, ...]) -> None:
    assert parse_sizes(text) == expected


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("abc", "Not a size"),
        ("40-", "Can't read size range"),
        ("-40", "Can't read size range"),
        ("44-40", "backwards"),
        ("4100", "looks wrong"),
        ("1-9999999", "looks wrong"),
        ("", "No sizes found"),
    ],
)
def test_bad_sizes_raise(text: str, message: str) -> None:
    with pytest.raises(CaptionError, match=message):
        parse_sizes(text)


@pytest.mark.parametrize(
    ("caption", "message"),
    [
        ("Nike Air Max", "Missing: Price, Sizes"),
        ("Nike Air Max\nSizes: 42", "Missing: Price"),
        ("Nike Air Max\nPrice: 3000", "Missing: Sizes"),
        ("   \n  ", "Caption is empty"),
        ("Price: 3000\nSizes: 42", "First line must be the product name"),
        ("Nike\nPrice: 3000\nPrice: 3200\nSizes: 42", "Price is written twice"),
        ("Nike\nPrice: 3000\nSizes: 42\nSizes: 43", "Sizes are written twice"),
    ],
)
def test_bad_caption_raises(caption: str, message: str) -> None:
    with pytest.raises(CaptionError, match=message):
        parse_caption(caption)


@pytest.mark.parametrize("mark", ["SOLD OUT", "sold out", "Sold out!", "  Sold Out.  "])
def test_sold_out_mark(mark: str) -> None:
    assert parse_caption(f"Nike\nPrice: 3000\nSizes: 42\n{mark}").sold_out is True


def test_sold_out_words_inside_a_sentence_are_description() -> None:
    product = parse_caption("Nike\nPrice: 3000\nSizes: 42\nAlmost sold out, order fast")

    assert product.sold_out is False
    assert product.description == "Almost sold out, order fast"


def test_label_is_case_and_space_insensitive() -> None:
    product = parse_caption("Nike\nPRICE : 3000\n sizes:42 ")

    assert (product.price, product.sizes) == (3000, (42,))


def test_unknown_labels_and_blank_lines_go_to_description() -> None:
    product = parse_caption("Nike\n\nPrice: 3000\nMaterial: leather\n\nSizes: 42\nTrue to size")

    assert product.description == "Material: leather\nTrue to size"
