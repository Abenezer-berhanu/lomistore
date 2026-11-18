"""Read Lomi Store channel post captions into product data.

Staff write captions like this:

    Nike Air Force 1 White
    Price: 3,500 ETB
    Sizes: 40, 41, 42-44
    Any other line becomes the description.
    SOLD OUT

This file has no Django or Telegram code on purpose. Plain functions that
take text and return data are the easiest code to test and to reuse.
"""

# LEARN: imports go at the top. Standard library first, then other packages,
#   then our own code, each group separated by a blank line.
import re
from dataclasses import dataclass

# LEARN: UPPER_CASE names are constants by convention. Python can't stop you
#   from changing them; the name tells other people "don't".
# SENIOR: no "magic numbers" inside functions. A named value explains itself
#   and is changed in one place.
MIN_SIZE = 16  # EU kids sizes start around here
MAX_SIZE = 50

# LEARN: re.compile() builds a regex object once, when the file is imported.
#   \d is a digit, [\d,]* is "digits or commas, any amount", [,\s]+ is
#   "one or more commas or spaces".
# BEGINNER: re.search(r"\d[\d,]*", value) written inside the function.
# WHY NOT: it works (Python caches patterns), but a named constant tells the
#   reader what the pattern is for without having to decode it.
PRICE_NUMBER = re.compile(r"\d[\d,]*")
SIZE_SEPARATOR = re.compile(r"[,\s]+")

SOLD_OUT_MARK = "sold out"


# LEARN: our own error type. It inherits from Exception, so it works with
#   try/except like any built-in error.
# SENIOR: callers can catch exactly our errors (`except CaptionError`) and
#   never hide real bugs by mistake. The messages are written for staff,
#   because the bot will send them to the admin group as they are.
# BEGINNER: raise ValueError("...") everywhere.
# WHY NOT: then `except ValueError` would also catch unrelated bugs, such as
#   a bad int() call somewhere else, and the bot would report a wrong reason.
class CaptionError(Exception):
    """Raised when a caption can't be read. The message is safe to show staff."""


# LEARN: @dataclass writes __init__, __repr__ (printing) and __eq__ (==) for us.
#   frozen=True: fields can't change after creation.
#   slots=True: uses less memory, and a typo like `product.prise = 1` raises
#   an error instead of silently creating a new attribute.
# SENIOR: parsed data is a "value object": it's created once and only read.
#   Freezing it means no other code can change it behind your back.
# BEGINNER: return a dict like {"name": ..., "price": ...}.
# WHY NOT: dict keys aren't checked. product["prise"] fails only when the
#   code runs, and VS Code can't autocomplete or type-check the keys.
@dataclass(frozen=True, slots=True)
class ParsedProduct:
    name: str
    # SENIOR: money is a whole number of birr, never a float.
    #   Floats can't store some values exactly (0.1 + 0.2 == 0.30000000000000004).
    price: int
    # SENIOR: a tuple, not a list, because a frozen object should hold
    #   values that can't be changed either. A list could still be modified.
    sizes: tuple[int, ...]
    description: str = ""
    sold_out: bool = False


def parse_price(value: str) -> int:
    """Return the price in birr from text like "3,500 ETB" or "Br 2,800"."""
    match = PRICE_NUMBER.search(value)
    # SENIOR: "guard clause". Handle the bad case first and leave, so the
    #   happy path below isn't nested inside an else.
    # BEGINNER:
    #   if match:
    #       ...all the real work, indented...
    #   else:
    #       raise ...
    # WHY NOT: every extra check adds another level of indentation, and the
    #   main logic ends up buried on the right.
    # LEARN: `is None`, not `== None`. None is a single object, and `is`
    #   checks "is it exactly that object".
    if match is None:
        raise CaptionError(f"Can't read price: {value.strip()!r}")

    price = int(match.group().replace(",", ""))
    if price <= 0:
        raise CaptionError("Price must be more than 0")
    return price


def parse_sizes(value: str) -> tuple[int, ...]:
    """Return sorted unique sizes from text like "40, 41 42-44"."""
    # SENIOR: a set removes duplicates as we go, so "42, 42" counts once.
    # BEGINNER: build a list, then check `if size not in sizes` before each append.
    # WHY NOT: `in` on a list checks every item one by one. A set checks
    #   instantly, and the intent ("unique sizes") is clear from the type.
    sizes: set[int] = set()
    for part in SIZE_SEPARATOR.split(value.strip()):
        # LEARN: "40, 41," splits into ['40', '41', '']. Empty parts are skipped.
        if not part:
            continue
        sizes.update(_expand_size_part(part))

    if not sizes:
        raise CaptionError("No sizes found")
    return tuple(sorted(sizes))


# LEARN: a name starting with _ means "private to this file". Python doesn't
#   enforce it; it tells others not to import it.
# SENIOR: small helpers with one job each. parse_sizes reads as a short story,
#   and each helper can be understood on its own.
def _expand_size_part(part: str) -> range:
    """Turn "42" into range(42, 43) and "40-42" into range(40, 43)."""
    # LEARN: partition always returns 3 parts: (before, separator, after).
    #   "40-42" gives ('40', '-', '42') and "42" gives ('42', '', '').
    # BEGINNER: start, end = part.split("-")
    # WHY NOT: split crashes with a confusing "not enough values to unpack"
    #   when there's no dash, or "too many" when there are two.
    start_text, dash, end_text = part.partition("-")
    if not dash:
        size = _to_size(part)
        return range(size, size + 1)

    if not start_text or not end_text:
        raise CaptionError(f"Can't read size range: {part!r}")

    # SENIOR: check the ends BEFORE building the range. A typo like "1-9999999"
    #   is rejected immediately instead of creating millions of numbers first.
    start, end = _to_size(start_text), _to_size(end_text)
    if start > end:
        raise CaptionError(f"Size range is backwards: {part!r}")
    # LEARN: range's end is NOT included, so +1 makes "40-42" include 42.
    return range(start, end + 1)


def _to_size(text: str) -> int:
    """Convert one size like "42" to an int and check it's a real shoe size."""
    try:
        size = int(text)
    except ValueError as err:
        # LEARN: `from err` keeps the original error attached. Logs then show
        #   both the friendly message and the real cause.
        raise CaptionError(f"Not a size: {text!r}") from err

    # LEARN: Python allows chained comparisons, like in math: a <= x <= b.
    # BEGINNER: if size < MIN_SIZE or size > MAX_SIZE:
    # WHY NOT: both are correct; the chained form reads like the rule itself.
    if not MIN_SIZE <= size <= MAX_SIZE:
        raise CaptionError(f"Size {size} looks wrong, allowed {MIN_SIZE} to {MAX_SIZE}")
    return size


def parse_caption(text: str) -> ParsedProduct:
    """Read a full channel post caption. Raises CaptionError if it can't."""
    # LEARN: list comprehension + walrus operator (:=). The walrus saves the
    #   stripped line in `stripped` while also checking it isn't empty.
    # BEGINNER:
    #   lines = []
    #   for line in text.splitlines():
    #       if line.strip():
    #           lines.append(line.strip())
    # WHY NOT: four lines for one idea, and strip() runs twice per line.
    lines = [stripped for line in text.splitlines() if (stripped := line.strip())]
    if not lines:
        raise CaptionError("Caption is empty")

    # LEARN: star unpacking. `name` gets the first item, `rest` gets a list
    #   of everything else. Like `const [name, ...rest] = lines` in JS.
    name, *rest = lines
    if _split_label(name)[0] in ("price", "size", "sizes"):
        raise CaptionError("First line must be the product name")

    # LEARN: `int | None` means "an int, or None until we find it".
    price: int | None = None
    sizes: tuple[int, ...] | None = None
    description: list[str] = []
    sold_out = False

    for line in rest:
        label, value = _split_label(line)
        # LEARN: `match` (Python 3.10+) compares one value against patterns.
        #   `"size" | "sizes"` means either one. `case _` is "anything else",
        #   and `if ...` after a case is an extra condition (a "guard").
        # BEGINNER: an if / elif / elif / else chain.
        # WHY NOT: an if/elif chain is equally professional; match reads like a
        #   table of rules, which helps once there are several labels.
        match label:
            case "price":
                # SENIOR: reject duplicates instead of silently keeping the last one.
                #   Two prices in one post is a staff mistake worth reporting.
                if price is not None:
                    raise CaptionError("Price is written twice")
                price = parse_price(value)
            case "size" | "sizes":
                if sizes is not None:
                    raise CaptionError("Sizes are written twice")
                sizes = parse_sizes(value)
            case _ if line.lower().strip(" !.") == SOLD_OUT_MARK:
                sold_out = True
            case _:
                description.append(line)

    # SENIOR: checking `price is None` here also teaches the type checker
    #   that after this block, price is an int (not None). This is called
    #   "type narrowing", so ParsedProduct(price=price) below type-checks.
    if price is None or sizes is None:
        missing = [label for label, found in (("Price", price), ("Sizes", sizes)) if found is None]
        raise CaptionError(f"Missing: {', '.join(missing)}")

    # SENIOR: keyword arguments. Reading the call tells you which value goes
    #   where, and changing the field order later can't silently swap values.
    # BEGINNER: ParsedProduct(name, price, sizes, "\n".join(description), sold_out)
    # WHY NOT: with 5 positional values it's easy to mix two of the same type.
    return ParsedProduct(
        name=name,
        price=price,
        sizes=sizes,
        description="\n".join(description),
        sold_out=sold_out,
    )


# SENIOR: returning a tuple lets the caller unpack both values in one line:
#   `label, value = _split_label(line)`.
def _split_label(line: str) -> tuple[str | None, str]:
    """Split "Price: 3,500" into ("price", " 3,500"). No colon gives (None, line)."""
    label, colon, value = line.partition(":")
    if not colon:
        return None, line
    return label.strip().lower(), value
