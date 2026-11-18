# Phase 0: Python foundations (reading guide)

**Built:** the caption parser, the first real Lomi Store code. It turns a channel post's text into product data (name, price, sizes, description, sold out). Every mistake staff can make gets a clear error message.

**Python you'll learn by reading it:** modules and packages, constants, compiled regex, custom exceptions, frozen dataclasses, type hints, guard clauses, sets, `partition`, chained comparisons, comprehensions with the walrus operator, star unpacking, `match` statements, keyword arguments, pytest fixtures, `parametrize`, `pytest.raises`.

---

## How to read the comments

Every important line has a short comment with one of these tags:

| Tag | Meaning |
|---|---|
| `LEARN:` | What this Python feature is and how it works |
| `SENIOR:` | Why a professional writes it this way |
| `BEGINNER:` | The simpler way you might write it |
| `WHY NOT:` | Why we don't use the beginner way here |

---

## 1. Run it first

Open a terminal in the project, activate the venv, install the dev packages, and run the tests:
```
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
pytest -v
```
Expected: the last line says **`37 passed`**.

Then play with the parser yourself:
```
python
>>> from catalog.caption import parse_caption
>>> parse_caption("Puma Suede\nPrice: 2,900 ETB\nSizes: 39-41")
>>> parse_caption("Puma Suede\nPrice: free\nSizes: 40")
>>> exit()
```
The first call returns a `ParsedProduct`. The second raises `CaptionError: Can't read price: 'free'`.

---

## 2. Reading order

### File: [catalog/caption.py](../catalog/caption.py)

| Lines | What it is | Focus on |
|---|---|---|
| 1 to 13 | Module docstring | Every file starts by saying what it's for. Notice *why* there's no Django code here. |
| 15 to 36 | Imports, constants, regex | Import order. UPPER_CASE constants. Why the regex is compiled once and given a name. |
| 39 to 48 | `CaptionError` | Why we make our own error class instead of using `ValueError`. |
| 51 to 70 | `ParsedProduct` dataclass | What `@dataclass` writes for you. `frozen` and `slots`. **Money as `int`, never float.** Tuple vs list. |
| 73 to 93 | `parse_price` | **Guard clause** (handle the bad case first, then return). `is None` vs `== None`. |
| 96 to 111 | `parse_sizes` | Using a `set` for unique values. How empty parts are skipped. |
| 114 to 139 | `_expand_size_part` | The `_` "private" prefix. `partition` vs `split`. **Validate before doing expensive work.** Why `range` needs `+1`. |
| 142 to 156 | `_to_size` | `try/except`, and `raise ... from err`. Chained comparison `a <= x <= b`. |
| 159 to 226 | `parse_caption` | The main function. Read it slowly: walrus `:=` (169), star unpacking (175), `int \| None` (180), `match` + guard (185 to 208), duplicate checks, **type narrowing** (212), keyword arguments (220). |
| 229 to 236 | `_split_label` | Returning a tuple so the caller can unpack two values at once. |

### File: [catalog/tests/test_caption.py](../catalog/tests/test_caption.py)

| Lines | What it is | Focus on |
|---|---|---|
| 1 to 15 | Docstring + imports | Importing several names with parentheses. |
| 18 to 32 | `full_caption` **fixture** | How pytest hands test data to a test by matching the parameter name. |
| 35 to 48 | First test | Good test names. Comparing one whole object vs five separate asserts. |
| 51 to 57 | Defaults test | `is False` vs `== False`. |
| 60 to 76 | `parametrize` | One test, many inputs. Look at how `pytest -v` names each case. |
| 79 to 92 | `pytest.raises` | **Always check the error message**, not only the error type. |
| 95 to 166 | The other tests | Read the input tables: they're the parser's rules, written as data. Try to guess each result before reading it. |

### Other new files

| File | Why it exists |
|---|---|
| [pyproject.toml](../pyproject.toml) | One config file for Python tools. Right now it holds pytest settings, so plain `pytest` works from the project root. |
| [requirements.txt](../requirements.txt) | Packages production needs. Empty until Django comes in Phase 2. |
| [requirements-dev.txt](../requirements-dev.txt) | Dev-only packages (pytest). It includes `requirements.txt` with `-r`. **Senior:** the server never installs test tools. |
| [.gitattributes](../.gitattributes) | Saves files with Linux line endings in git. Windows line endings break scripts on the Hetzner server. |
| `catalog/__init__.py`, `catalog/tests/__init__.py` | Empty files that make the folders **packages**, so `from catalog.caption import ...` works. In Phase 2 `catalog` becomes a Django app, and this code is already in place. |

---

## 3. Check yourself (optional)

Try to answer these without looking. Then check the comments.

1. Why does `CaptionError` exist when `ValueError` already does?
2. Why is `price` an `int` and not a `float`?
3. Why does `_expand_size_part` check both ends **before** calling `range`?
4. What does `partition` return for `"42"`? And for `"40-42"`?
5. Why does `test_bad_price_raises` use `match=`?

**Small exercise:** add a test case where `"Sizes: 40/41"` should raise `CaptionError`. Run `pytest`. Does it pass? Why, or why not? Tell me what you find.

---

## 4. Done

- [x] Caption parser written, 37 tests passing
- [x] Committed: `Phase 0: caption parser with tests`
- [ ] You read the files and ran the commands above
- [ ] You asked me about anything that wasn't clear
