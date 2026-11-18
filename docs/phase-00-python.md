# Phase 0: Python foundations

**Goal:** fill the Python gaps you'll need for Django, and build the first real piece of Lomi Store: the **caption parser**, which turns a channel post's text into product data.

**You already know:** data types, variables, lists, dicts, loops, if/else, classes, methods.
**You'll learn here:** virtual environments, pip, modules and imports, `__name__`, f-strings, string methods, comprehensions, type hints, custom exceptions, dataclasses, regex, pytest, git basics for this repo.

**Where the code goes:** `learning/phase0/`. In Phase 3 we move `caption.py` into the Django app. Moving code is a lesson too.

**How to report:** after each step, send me `Step 0.X done` + your code + what the terminal printed. I'll review it before you continue.

---

## Step 0.1: Set up the project

### Read
- A **virtual environment** (`.venv`) is a private copy of Python just for this project. Packages you install go inside it, not into your whole computer. It's like `node_modules`, but for the Python interpreter and its packages together.
- **pip** is Python's `npm`. `requirements.txt` is like the `dependencies` part of `package.json`.
- The `lomi_fashion` folder is currently inside the big `C:\abulo` git repo. We'll make it **its own repo** so Lomi Store has its own clean history.

### Type
Open the VS Code terminal (PowerShell) in `C:\abulo\work\lomi_fashion` and run these one at a time:

1. `py -3.13 --version`
2. `git init`
3. `py -3.13 -m venv .venv`
4. `.venv\Scripts\Activate.ps1`
   - If you get *"running scripts is disabled on this system"*, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, answer `Y`, then try again.
5. `python --version`
6. `python -c "import sys; print(sys.prefix)"`
7. `python -m pip install --upgrade pip`
8. `python -m pip install pytest`
9. `pytest --version`

Now create these files in VS Code (by hand, not with a terminal command):

- **`.gitignore`** in the project root, with one entry per line: `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.env`, `db.sqlite3`
- **`requirements.txt`** in the project root with one line: `pytest==` followed by the version that step 9 printed (for example `pytest==8.4.2`).

Finally, in VS Code press `Ctrl+Shift+P`, choose **Python: Select Interpreter**, and pick the one that has `.venv` in its path. Install the **Python** extension by Microsoft if VS Code asks.

### Check
| Command | Expected |
|---|---|
| `py -3.13 --version` | `Python 3.13.x` |
| `git init` | `Initialized empty Git repository in C:/abulo/work/lomi_fashion/.git/` |
| after activate | Your prompt starts with `(.venv)` |
| `python -c "import sys; print(sys.prefix)"` | A path ending in `lomi_fashion\.venv` |
| `pytest --version` | `pytest 8.x.x` or `pytest 9.x.x` |
| `git status` | Lists `.gitignore`, `docs/`, `requirements.txt` as untracked. **`.venv` must NOT be listed.** |

> Every time you open a new terminal, activate the venv again (step 4). If `(.venv)` isn't in the prompt, you're using the wrong Python.

---

## Step 0.2: Modules, imports and `__name__`

### Read
- Every `.py` file is a **module**. You can import functions from it like `import { greet } from "./greet"` in JS, but in Python it's written `from greet import greet`.
- There's no `export` keyword. Everything at the top level of a file can be imported.
- Python sets the variable `__name__` in every file. When you **run** the file directly, it's `"__main__"`. When the file is **imported**, it's the module name (`"greet"`).
- That's why you'll often see `if __name__ == "__main__":`. The code under it runs only when you execute the file directly, not when you import it.
- Python style uses `snake_case` for functions and variables (`parse_price`, not `parsePrice`) and `PascalCase` for classes.

### Type
Create the folder `learning/phase0/`.

**File `learning/phase0/greet.py`:**
1. On the first line, print the text `greet.py loaded, __name__ is ` followed by the value of `__name__`. Use an f-string: `f"... {__name__}"` (the same idea as a JS template literal).
2. Define a function `greet` that takes a parameter `name` and **returns** (doesn't print) the text `Welcome to Lomi Store, <name>!`, built with an f-string.
3. At the bottom, add an `if __name__ == "__main__":` block that prints `greet("Abebe")`.

**File `learning/phase0/use_greet.py`:**
1. Import `greet` from the `greet` module.
2. Print `greet("Sara")`.

### Check
```
python learning/phase0/greet.py
```
Expected:
```
greet.py loaded, __name__ is __main__
Welcome to Lomi Store, Abebe!
```
```
python learning/phase0/use_greet.py
```
Expected:
```
greet.py loaded, __name__ is greet
Welcome to Lomi Store, Sara!
```
Notice that `Abebe` did **not** print the second time. Explain to me in one sentence why.

Then **delete the print line at the top of `greet.py`**. Code that runs on import (a "side effect") is a bad habit. We only added it to see `__name__`.

---

## Step 0.3: Strings, f-strings, `enumerate`, unpacking

### Read
Useful string methods (all return a **new** string, because strings never change in place):
- `.strip()` removes spaces and newlines from both ends.
- `.lower()` returns a lowercase copy.
- `.startswith("x")` checks the beginning. It also accepts a tuple: `.startswith(("a", "b"))` means "starts with a OR b".
- `.splitlines()` splits the text into a list of lines.
- `.split(":", 1)` splits on `:` **at most once**. `"Price: 3:00".split(":", 1)` gives `['Price', ' 3:00']`.
- `enumerate(items, start=1)` gives you `(number, item)` pairs while looping, like `items.forEach((item, i) => ...)` in JS.
- **Unpacking:** `label, value = ["Price", " 3,500"]` puts each item in its own variable, like JS destructuring `const [label, value] = ...`.
- `repr(x)`, or `{x!r}` inside an f-string, shows a value with its quotes, so hidden spaces become visible.

### Type
**File `learning/phase0/strings_practice.py`:**
1. Create a variable `caption` with exactly this value (`\n` means new line):
   `"  Nike Air Force 1 White  \n\nPrice: 3,500 ETB\nSizes: 40, 41, 42\n"`
2. Create `lines` by calling `.strip()` and then `.splitlines()` on `caption`. Print `lines`.
3. Print an empty line, using `print()` with nothing inside.
4. Loop over `lines` with `enumerate(..., start=1)`, getting `number` and `line`.
   - Strip the line.
   - If the line is empty, `continue` (skip to the next one).
   - Otherwise print `f"{number}: {line}"`.
5. Print an empty line.
6. Loop over `lines` again. If the line, lowercased and stripped, starts with `"price:"`:
   - Split the stripped line on `":"` at most once, and unpack it into `label` and `value`.
   - Print `f"Price text is {value.strip()!r}"`.

### Check
```
python learning/phase0/strings_practice.py
```
Expected:
```
['Nike Air Force 1 White  ', '', 'Price: 3,500 ETB', 'Sizes: 40, 41, 42']

1: Nike Air Force 1 White
3: Price: 3,500 ETB
4: Sizes: 40, 41, 42

Price text is '3,500 ETB'
```
Question for you: why does the first item still have two spaces at the end, even though we called `.strip()`?

---

## Step 0.4: Comprehensions, sets, `sorted`

### Read
A **list comprehension** builds a list in one line. It's Python's version of `map` + `filter`:

| JavaScript | Python |
|---|---|
| `parts.map(p => Number(p))` | `[int(p) for p in parts]` |
| `sizes.filter(s => s >= 42)` | `[s for s in sizes if s >= 42]` |
| `Object.fromEntries(sizes.map(s => [s, 0]))` | `{s: 0 for s in sizes}` |

- `set(items)` removes duplicates (no order).
- `sorted(items)` returns a new sorted **list**.
- `int(" 40")` works. `int()` ignores spaces around the number.

### Type
**File `learning/phase0/comprehensions_practice.py`:**
1. `raw = "42, 40, 41, 42"`
2. `parts`: split `raw` on `","`. Print it.
3. `sizes`: a list comprehension that turns every part into an `int`. Print it.
4. `unique_sizes`: `sizes` without duplicates, sorted. Print it.
5. `big_sizes`: a comprehension with an `if` that keeps only sizes `>= 42` from `sizes`. Print it.
6. `stock`: a **dict** comprehension mapping every size in `unique_sizes` to `0`. Print it.

### Check
```
python learning/phase0/comprehensions_practice.py
```
Expected:
```
['42', ' 40', ' 41', ' 42']
[42, 40, 41, 42]
[40, 41, 42]
[42, 42]
{40: 0, 41: 0, 42: 0}
```

---

## Step 0.5: Type hints

### Read
Type hints are like TypeScript types, but **Python doesn't enforce them when the code runs**. They're for you, VS Code, and tools like `mypy`. Professional Python code uses them everywhere, and Django projects do too.

```python
def greet(name: str) -> str: ...          # takes a str, returns a str
sizes: list[int] = []                     # a list of ints
price: int | None = None                  # int or None (like number | null)
sizes_fixed: tuple[int, ...] = (40, 41)   # a tuple of any number of ints
```
- `None` is Python's `null`. Check for it with `is None` and `is not None`, never `== None`.
- A **tuple** `(40, 41)` is like a list that can't be changed.

### Type
Add type hints to `greet` in `greet.py`: the parameter `name` is a `str`, and it returns a `str`.

### Check
Run `python learning/phase0/greet.py` again. It should print only `Welcome to Lomi Store, Abebe!`. Hover over `greet` in `use_greet.py`, and VS Code should show `(name: str) -> str`.

---

## Step 0.6: Exceptions and custom exceptions

### Read
- `try / except` is JS `try / catch`. `raise` is `throw`.
- Catch **specific** errors (`except ValueError`), never everything with a bare `except:`.
- You create your own error type by making a class that inherits from `Exception`. That way, the code calling yours can catch exactly **your** errors.
- `raise NewError(...) from err` keeps the original error attached, which makes debugging much easier.

### Type
**File `learning/phase0/exceptions_practice.py`:**
1. Create a class `CaptionError` that inherits from `Exception`. Its body is only a docstring: `"""Raised when a channel post caption can't be read."""`
2. Create a function `parse_int` that takes `text: str` and returns `int`:
   - In a `try` block, return `int(text)`.
   - `except ValueError as err:` raise a `CaptionError` with the message `f"Not a number: {text!r}"`, using `from err`.
3. Loop over the list `["40", " 41 ", "abc"]`. For each value:
   - In a `try`, print `parse_int(value)`.
   - `except CaptionError as error:` print `f"Error: {error}"`.

### Check
```
python learning/phase0/exceptions_practice.py
```
Expected:
```
40
41
Error: Not a number: 'abc'
```

---

## Step 0.7: Dataclasses

### Read
A **dataclass** is a class that mainly holds data. Python writes `__init__`, printing and `==` comparison for you. It's close to a TypeScript `interface` plus a constructor.

```python
from dataclasses import dataclass

@dataclass(frozen=True)       # frozen = fields can't be changed after creation
class Point:
    x: int
    y: int = 0                # default value (fields with defaults go last)
```
`@dataclass` is a **decorator**: it takes the class and adds features to it. Django uses decorators a lot.

### Type
**File `learning/phase0/dataclass_practice.py`:**
1. Import `dataclass` and `FrozenInstanceError` from `dataclasses`.
2. Create a frozen dataclass `Shoe` with fields: `name: str`, `price: int`, `sizes: tuple[int, ...]`, and `sold_out: bool` with default `False`.
3. Create `shoe = Shoe("Air Force 1", 3500, (40, 41))` and print it.
4. Print whether `shoe == Shoe("Air Force 1", 3500, (40, 41))`.
5. In a `try`, set `shoe.price = 3000`. `except FrozenInstanceError:` print `Can't change a frozen dataclass`.

### Check
```
python learning/phase0/dataclass_practice.py
```
Expected:
```
Shoe(name='Air Force 1', price=3500, sizes=(40, 41), sold_out=False)
True
Can't change a frozen dataclass
```
Question for you: why did I make `sizes` a `tuple` and not a `list` in a frozen dataclass?

---

## Step 0.8: Regular expressions (`re`)

### Read
Regex in Python lives in the `re` module. Always write patterns as **raw strings**, `r"..."`, so backslashes stay as they are.
- `re.search(pattern, text)` finds the first match, or returns `None`. `match.group()` gives the matched text.
- `re.split(pattern, text)` splits on every match.
- `\d` is a digit, `[\d,]*` is "any number of digits or commas", and `[,\s]+` is "one or more commas or spaces".

### Type
**File `learning/phase0/regex_practice.py`:**
1. Import `re`.
2. Loop over `["3,500 ETB", "3500 birr", "Br 2,800", "free"]`:
   - Search with the pattern `r"\d[\d,]*"`.
   - If there's no match (`is None`), print `f"{text!r} -> no number"`.
   - Otherwise, take the matched text, remove the commas with `.replace(",", "")`, convert it to `int`, and print `f"{text!r} -> {number}"`.
3. Print `re.split(r"[,\s]+", "40, 41 42,43")`.
4. Print `re.split(r"[,\s]+", "40, 41,")`.

### Check
```
python learning/phase0/regex_practice.py
```
Expected:
```
'3,500 ETB' -> 3500
'3500 birr' -> 3500
'Br 2,800' -> 2800
'free' -> no number
['40', '41', '42', '43']
['40', '41', '']
```
Notice the empty `''` at the end of the last line. Our parser will have to skip it.

---

## Step 0.9: pytest basics

### Read
- pytest finds files named `test_*.py` and runs functions named `test_*`.
- You check things with plain `assert`. pytest shows a detailed diff when an assert fails.
- Test that something raises an error:
  ```python
  with pytest.raises(CaptionError, match="Missing"):
      do_something()
  ```
- Run one test with many inputs using **parametrize**:
  ```python
  @pytest.mark.parametrize(("name", "expected"), [
      ("Sara", "Welcome to Lomi Store, Sara!"),
      ("Abebe", "Welcome to Lomi Store, Abebe!"),
  ])
  def test_greet(name: str, expected: str) -> None:
      assert greet(name) == expected
  ```

### Type
**File `learning/phase0/test_greet.py`:**
1. Import `pytest`, and import `greet` from `greet`.
2. Write the parametrized `test_greet` exactly like the example above.

### Check
```
pytest learning/phase0 -v
```
Expected (the end of the output; the file path in front may look a little different):
```
...test_greet.py::test_greet[Sara-Welcome to Lomi Store, Sara!] PASSED
...test_greet.py::test_greet[Abebe-Welcome to Lomi Store, Abebe!] PASSED
==== 2 passed in 0.0Xs ====
```
Now **break it on purpose**: change `Welcome` to `Hello` inside `greet.py`, run pytest again, and read the failure output carefully. Then fix it. Learning to read a failing test is a core skill.

---

## Step 0.10: The real thing, `caption.py`

This is Lomi Store's first production code. Staff will write captions like:
```
Nike Air Force 1 White
Price: 3,500 ETB
Sizes: 40, 41, 42-44
Original, made in Vietnam
SOLD OUT
```

### Type
**File `learning/phase0/caption.py`.** At the very top, write a module docstring: `"""Parse Lomi Store channel post captions into product data."""`. Then:

**1. Imports:** `re`, and `dataclass` from `dataclasses`.

**2. Constants** (Python constants are UPPER_CASE by convention):
- `MIN_SIZE = 16` and `MAX_SIZE = 50` (EU shoe sizes, kids to large adults).

**3. `class CaptionError(Exception)`** with a docstring, the same as in step 0.6.

**4. `@dataclass(frozen=True) class ParsedProduct`** with fields:
- `name: str`
- `price: int` (in ETB)
- `sizes: tuple[int, ...]`
- `description: str = ""`
- `sold_out: bool = False`

**5. `def parse_price(value: str) -> int`**, with a docstring explaining what it does:
- Search `value` with the pattern from step 0.8.
- If there's no match, raise `CaptionError(f"Can't read price: {value!r}")`.
- Turn the match into an `int` (remove the commas first).
- If the number is `0` or less, raise `CaptionError("Price must be more than 0")`.
- Return the number.

**6. `def parse_sizes(value: str) -> tuple[int, ...]`**, with a docstring:
- Create an empty `sizes: list[int] = []`.
- Split `value.strip()` with the pattern `r"[,\s]+"` into `parts`.
- Open a `try` block, and inside it loop over `parts`:
  - If `part` is empty, `continue`.
  - If `"-"` is in `part`, it's a range:
    - Split it on `"-"` at most once and unpack it into `start_text, end_text`.
    - Convert both to `int` as `start` and `end`.
    - If `start > end`, raise `CaptionError(f"Size range is backwards: {part!r}")`.
    - Add every size from `start` to `end` **including `end`** to `sizes`. Use `range(...)` and `.extend(...)`. Think carefully about `range`'s end value.
  - Else, append `int(part)` to `sizes`.
- `except ValueError as err:` raise `CaptionError(f"Can't read sizes: {value!r}") from err`.
- After the try/except: if `sizes` is empty, raise `CaptionError("No sizes found")`.
- Loop over `sizes`. If any size is smaller than `MIN_SIZE` or bigger than `MAX_SIZE`, raise `CaptionError(f"Size {size} looks wrong")`.
- Return the sizes **without duplicates, sorted, as a tuple**.

**7. `def parse_caption(text: str) -> ParsedProduct`**, with a docstring:
- Build `lines` with a list comprehension: each line from `text.splitlines()`, stripped, keeping only lines that aren't empty after stripping.
- If `lines` is empty, raise `CaptionError("Caption is empty")`.
- `name` is the first line.
- If the lowercased `name` starts with `"price:"`, `"sizes:"` or `"size:"` (use the tuple form of `startswith`), raise `CaptionError("First line must be the product name")`.
- Set up, with type hints:
  - `price: int | None = None`
  - `sizes: tuple[int, ...] | None = None`
  - `description_lines: list[str] = []`
  - `sold_out = False`
- Loop over every line **except the first** (use slicing, `lines[1:]`):
  - Make `lower` the lowercased line.
  - If `lower` starts with `"price:"`, set `price` to `parse_price(...)` of the part after the first `":"`.
  - Elif `lower` starts with `"sizes:"` or `"size:"`, set `sizes` to `parse_sizes(...)` of the part after the first `":"`.
  - Elif `lower` is exactly `"sold out"`, set `sold_out = True`.
  - Else, append the line to `description_lines`.
- Create `missing: list[str] = []`. If `price is None`, append `"Price"`. If `sizes is None`, append `"Sizes"`.
- If `missing` isn't empty, raise `CaptionError("Missing: " + ", ".join(missing))`.
- Return a `ParsedProduct` using **keyword arguments** (`name=name, price=price, ...`). For `description`, join `description_lines` with `"\n"`.

### Type the tests
**File `learning/phase0/test_caption.py`.** Import `pytest`, and from `caption` import `CaptionError`, `ParsedProduct`, `parse_caption`, `parse_price`, `parse_sizes`. Write these tests:

1. `test_parses_full_caption`: use the 5-line example caption above, and assert the result **equals** a full `ParsedProduct(...)` you write by hand. The sizes should be `(40, 41, 42, 43, 44)`.
2. `test_price_formats`, **parametrized** with `("3500", 3500)`, `("3,500 ETB", 3500)`, `("3500 birr", 3500)`, `("Br 2,800", 2800)`.
3. `test_price_without_number_raises`: `parse_price("free")` raises `CaptionError`.
4. `test_price_zero_raises`: `parse_price("0")` raises `CaptionError` with `match="more than 0"`.
5. `test_sizes_formats`, **parametrized** with:
   - `"40, 41, 42"` gives `(40, 41, 42)`
   - `"40 41 42"` gives `(40, 41, 42)`
   - `"42, 40, 42"` gives `(40, 42)`
   - `"39-42"` gives `(39, 40, 41, 42)`
   - `"38, 40-41"` gives `(38, 40, 41)`
   - `"40, 41,"` gives `(40, 41)`
6. `test_bad_sizes_raise`, **parametrized** with `"abc"`, `"40-"`, `"44-40"`, `"4100"`, `""`. Each raises `CaptionError`.
7. `test_missing_price_and_sizes`: the caption `"Nike Air Max"` raises with `match="Missing: Price, Sizes"`.
8. `test_empty_caption_raises`: `"   \n  "` raises with `match="empty"`.
9. `test_first_line_must_be_name`: a caption starting with `"Price: 3000"` raises with `match="First line"`.
10. `test_sold_out_line`: a valid caption that includes a line `sold out` (lowercase) gives `sold_out is True`. Check it with `is True`, not `== True`.
11. `test_description_keeps_extra_lines`: two extra lines end up in `description` joined by `"\n"`.
12. `test_size_singular_label`: `"Size: 42"` works too.

Add `-> None` to every test function. That's normal professional style.

### Check
```
pytest learning/phase0 -v
```
Expected: every test `PASSED`, ending with **`26 passed`** (2 from greet + 24 from caption, if you wrote exactly the tests listed).

Optional: play with your parser by hand:
```
python -i learning/phase0/caption.py
>>> parse_caption("Puma Suede\nPrice: 2,900\nSizes: 39-41")
>>> parse_caption("Puma Suede")
>>> exit()
```

---

## Step 0.11: Commit

### Type
```
git add .
git status
git commit -m "Phase 0: Python practice and caption parser with tests"
git log --oneline
```

### Check
- `git status` (before the commit) lists the files in `docs/`, `learning/phase0/`, `.gitignore` and `requirements.txt`. There's **no** `.venv` and **no** `__pycache__`.
- `git log --oneline` shows one commit.

---

## Done when

- [ ] All checks above match
- [ ] `pytest learning/phase0 -v` shows 26 passed
- [ ] You answered the 3 questions (steps 0.2, 0.3, 0.7)
- [ ] Committed
- [ ] "What I learned" filled in below

## What I learned

_(Write this yourself in your own words: 5 to 10 bullet points. What was new, what surprised you, what was hard.)_

-
