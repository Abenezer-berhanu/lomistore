"""Turn the many ways people write phone numbers into one format: +2519XXXXXXXX."""

import re

# Ethio telecom numbers start with 9, Safaricom with 7. Accepts 0911..., 911..., 251911..., +251911...
_ETHIOPIAN = re.compile(r"^(?:\+?251|0)?([79]\d{8})$")
_INTERNATIONAL = re.compile(r"^\+[1-9]\d{7,14}$")
_SEPARATORS = re.compile(r"[\s\-().]")


def normalize_phone(raw: str) -> str | None:
    """Return the phone as +251XXXXXXXXX (or +<country><number>), or None if it isn't one."""
    cleaned = _SEPARATORS.sub("", raw)
    if match := _ETHIOPIAN.match(cleaned):
        return f"+251{match.group(1)}"
    if _INTERNATIONAL.match(cleaned):
        return cleaned
    return None
