# What this project teaches

Every topic used to build Lomi Store, in a sensible learning order. For each one: what it is, and where to see it in this project. Tick them off one by one.

How to study one topic:
1. Read the "what it is" line, then search the official docs or ask me "explain <topic> with an example".
2. Open the file in the "See it in" column and find it in real code.
3. Change something small, run `pytest`, and see what breaks.

Good references:
- Python tutorial: https://docs.python.org/3/tutorial/
- Django tutorial (do all 8 parts): https://docs.djangoproject.com/en/5.2/intro/tutorial01/
- Channels tutorial: https://channels.readthedocs.io/en/latest/tutorial/
- Telegram Bot API: https://core.telegram.org/bots/api
- Docker get started: https://docs.docker.com/get-started/

---

## 1. Python language

| | Topic | What it is | See it in |
|---|---|---|---|
| [ ] | f-strings | `f"Price: {price:,} ETB"` puts values into text; `:,` adds thousands commas | `telegram_bot/handlers.py` |
| [ ] | String methods | `strip`, `lower`, `split`, `partition`, `startswith`, `removeprefix` | `catalog/caption.py` |
| [ ] | list, dict, set, tuple | The four main collections. A set has no duplicates, a tuple can't change | `catalog/caption.py` |
| [ ] | Comprehensions | `[x for x in items if ...]` builds a list in one line (like JS `map` + `filter`) | `catalog/caption.py`, `handlers.py` |
| [ ] | Slicing | `items[1:]`, `buttons[i : i + 4]` take a part of a list | `handlers.py` (size button rows) |
| [ ] | Unpacking | `a, b = pair` and `first, *rest = items` | `catalog/caption.py` |
| [ ] | Walrus `:=` | Assign and test in one step: `if match := pattern.match(text):` | `handlers.py`, `orders/phone.py` |
| [ ] | Functions | Default values, keyword arguments, `**params` (any number of named arguments) | `telegram_bot/client.py` |
| [ ] | Type hints | `str \| None`, `list[int]`, `dict[str, Any]`, `-> None` | Everywhere |
| [ ] | Exceptions | `try/except`, `raise`, custom error classes, `raise ... from err` | `catalog/caption.py`, `client.py` |
| [ ] | Classes | `__init__`, `self`, methods, inheritance (`class CaptionError(Exception)`) | `client.py` |
| [ ] | Dataclasses | Classes for data with `__init__`, `==` and printing written for you | `catalog/caption.py` |
| [ ] | Decorators | `@something` above a function or class adds behaviour to it | `@dataclass`, `@cache`, `@receiver`, `@admin.register` |
| [ ] | Modules and packages | Every `.py` file is a module; a folder with `__init__.py` is a package | Every app folder |
| [ ] | `if __name__ == "__main__"` | Code that runs only when the file is run directly | `manage.py` |
| [ ] | Regular expressions | Patterns for finding text: `\d`, `[,\s]+`, groups, `re.compile` | `catalog/caption.py`, `orders/phone.py` |
| [ ] | `match` statement | Compare one value against several patterns (Python 3.10+) | `catalog/caption.py` |
| [ ] | `with` (context managers) | Run setup and cleanup around a block automatically | `transaction.atomic()` in `handlers.py` |
| [ ] | lambda | A tiny unnamed function | `orders/signals.py` |
| [ ] | `functools.cache` | Remember a function's result so it only runs once | `client.py` (`get_client`) |
| [ ] | Protocol | "Anything with these methods fits", which lets tests pass a fake | `client.py` (`Bot`) |
| [ ] | async / await | Code that waits for network without blocking other work | `orders/consumers.py` |

## 2. Python tools

| | Topic | What it is | See it in |
|---|---|---|---|
| [ ] | Virtual environment | A private Python + packages per project (`.venv`) | `.venv/` |
| [ ] | pip and requirements | Installing packages; pinning exact versions | `requirements.txt`, `requirements-dev.txt` |
| [ ] | pyproject.toml | One config file for Python tools | `pyproject.toml` |
| [ ] | pytest basics | `test_*` functions with plain `assert` | `catalog/tests/` |
| [ ] | Fixtures | Reusable test setup handed to tests by parameter name | `conftest.py` |
| [ ] | parametrize | One test, many inputs | `catalog/tests/test_caption.py` |
| [ ] | `pytest.raises` | Test that code raises the right error | `catalog/tests/test_caption.py` |
| [ ] | monkeypatch | Swap a function for a fake during one test | `telegram_bot/tests/test_webhook.py` |
| [ ] | pytest-django | `db`, `client`, `admin_client`, `admin_user` fixtures | `orders/tests/test_dashboard.py` |

## 3. Django

| | Topic | What it is | See it in |
|---|---|---|---|
| [ ] | Project vs app | `config/` is the project (settings, URLs); `catalog`, `orders`, `telegram_bot` are apps | Folder layout |
| [ ] | manage.py | The command tool: `runserver`, `migrate`, `createsuperuser`, ... | `manage.py` |
| [ ] | Settings and env vars | Secrets come from the environment, never from code | `config/settings.py` |
| [ ] | URLs | `path()` and `include()` map addresses to views | `config/urls.py` |
| [ ] | Function views | A function that takes a request and returns a response | `orders/views.py`, `telegram_bot/views.py` |
| [ ] | Decorators on views | `@require_POST`, `@csrf_exempt`, `@staff_member_required` | `telegram_bot/views.py` |
| [ ] | Templates | HTML with `{{ value }}`, `{% url %}`, `json_script` | `orders/templates/orders/dashboard.html` |
| [ ] | Models and fields | Python classes that become database tables | `catalog/models.py`, `orders/models.py` |
| [ ] | Relationships | `ForeignKey` with `PROTECT` / `SET_NULL` | `orders/models.py` |
| [ ] | TextChoices | A fixed list of allowed values (order status) | `orders/models.py` |
| [ ] | Model Meta | `ordering`, `indexes` | `orders/models.py` |
| [ ] | Properties on models | Computed values like `product.order_url` | `catalog/models.py` |
| [ ] | Migrations | Files that change the database step by step (`makemigrations`, `migrate`) | `*/migrations/` |
| [ ] | ORM queries | `get`, `filter`, `first`, `count`, slicing `[:50]` | `handlers.py`, `orders/views.py` |
| [ ] | `update_or_create`, `get_or_create` | Create a row, or update it if it exists | `handlers.py`, `telegram_bot/views.py` |
| [ ] | `select_related` | Load related rows in one query (avoids the "N+1" problem) | `orders/views.py`, `orders/admin.py` |
| [ ] | Transactions | `atomic()` = all or nothing; `select_for_update()` locks a row | `handlers.py` (`place_order`) |
| [ ] | `on_commit` | Run code only after the data is really saved | `orders/signals.py` |
| [ ] | Signals | Run code when something happens, e.g. after an order is saved | `orders/signals.py`, `orders/apps.py` |
| [ ] | Django Admin | `list_display`, `list_editable`, `list_filter`, `search_fields`, actions, inlines, read-only fields | `catalog/admin.py`, `orders/admin.py` |
| [ ] | Users, staff, permissions | Who can log in and what they can change | `docs/DEPLOY.md` Part 5 |
| [ ] | Management commands | Your own `manage.py <command>` | `telegram_bot/management/commands/telegram_setup.py` |
| [ ] | Static files | Admin CSS/JS collected and served by WhiteNoise | `config/settings.py`, `Dockerfile` |
| [ ] | Security settings | CSRF, `ALLOWED_HOSTS`, secure cookies, `check --deploy` | `config/settings.py` |
| [ ] | Separate test settings | Tests never touch real services | `config/settings_test.py` |

## 4. Web and APIs

| | Topic | What it is | See it in |
|---|---|---|---|
| [ ] | HTTP basics | Methods (GET/POST), status codes (200, 302, 400, 403, 405), headers | `telegram_bot/views.py` |
| [ ] | JSON | The data format Telegram sends and receives | `telegram_bot/client.py` |
| [ ] | REST vs RPC | REST = resources + HTTP verbs (`GET /orders/12`). Telegram's API is RPC style (`POST /sendMessage`). Learn both. | `client.py` |
| [ ] | HTTP client | Calling another API from Python with `httpx` | `client.py` |
| [ ] | Webhooks vs polling | Telegram calls us, instead of us asking Telegram every second | `telegram_bot/views.py` |
| [ ] | Shared secrets | Checking a secret header with `constant_time_compare` | `telegram_bot/views.py` |
| [ ] | Idempotency | Handling the same request twice without doing the work twice | `telegram_bot/models.py` (`ProcessedUpdate`) |
| [ ] | XSS | Never put user text into HTML as code; use `textContent` | `dashboard.html` |

## 5. Real-time (WebSockets)

| | Topic | What it is | See it in |
|---|---|---|---|
| [ ] | WebSocket | A connection that stays open, so the server can push messages | `dashboard.html` (`new WebSocket`) |
| [ ] | WSGI vs ASGI | WSGI = one request at a time per worker; ASGI also supports long connections | `config/asgi.py` |
| [ ] | Django Channels | WebSockets in Django | `orders/consumers.py`, `orders/routing.py` |
| [ ] | Consumers | Like a view, but for a WebSocket connection | `orders/consumers.py` |
| [ ] | Groups and channel layer | Send one message to every open dashboard | `orders/live.py` |
| [ ] | Redis | Fast in-memory store; carries messages between processes | `compose.yaml`, `config/settings.py` |
| [ ] | `async_to_sync` | Call async code from normal (sync) code | `orders/live.py` |
| [ ] | Origin check and auth on sockets | Only staff, only from our own site | `config/asgi.py`, `consumers.py` |
| [ ] | Reconnect with backoff | Retry after 1s, 2s, 4s ... instead of hammering the server | `dashboard.html` |

## 6. Telegram bots

| | Topic | What it is | See it in |
|---|---|---|---|
| [ ] | Updates | Every event (message, button tap, channel post) arrives as JSON | `telegram_bot/handlers.py` |
| [ ] | Deep links | `t.me/bot?start=p45` opens the bot with data | `catalog/models.py` (`order_url`) |
| [ ] | Inline keyboards | Buttons under a message (URL buttons, callback buttons) | `handlers.py` |
| [ ] | Callback queries | What arrives when someone taps a callback button | `handlers.py` (`handle_callback`) |
| [ ] | Reply keyboard and `request_contact` | The "Share my phone number" button | `handlers.py` (`ask_for_phone`) |
| [ ] | file_id | Reuse a photo already on Telegram without storing it | `catalog/models.py` |
| [ ] | Channel admin rights | Why the bot needs "Edit messages of others" | `docs/DEPLOY.md` |
| [ ] | setWebhook with secret_token | How Telegram knows where to send updates | `telegram_setup.py` |

## 7. Databases

| | Topic | What it is | See it in |
|---|---|---|---|
| [ ] | SQLite vs PostgreSQL | File database for laptops; real server database for production | `config/settings.py` |
| [ ] | Primary key, unique, foreign key | How rows are identified and linked | `*/models.py` |
| [ ] | Indexes | Make common searches fast | `orders/models.py` |
| [ ] | JSON field | Store a list (sizes) inside one column | `catalog/models.py` |
| [ ] | Row locking | Stop two requests changing the same row at once | `handlers.py` |
| [ ] | Snapshot data | Copy the price into the order, so later price changes don't rewrite history | `orders/models.py` |
| [ ] | Backups | `pg_dump`, and restoring from it | `docs/DEPLOY.md` Part 6 |

## 8. Servers and DevOps

| | Topic | What it is | See it in |
|---|---|---|---|
| [ ] | Linux shell basics | `cd`, `ls`, `nano`, `cat`, pipes `\|`, `sudo` | `docs/DEPLOY.md` |
| [ ] | SSH | Logging into the server from your laptop | `docs/DEPLOY.md` |
| [ ] | Ports | What listens where; `ss -tlnp`; `127.0.0.1` vs public | `docs/DEPLOY.md` Step 2 |
| [ ] | Docker image and container | Image = packaged app; container = a running copy | `Dockerfile` |
| [ ] | Dockerfile layers | Why requirements are installed before copying code | `Dockerfile` |
| [ ] | docker compose | Several containers together: services, volumes, healthchecks, depends_on | `compose.yaml` |
| [ ] | Environment files | Secrets in `.env`, never in git | `.env.example` |
| [ ] | DNS | How `bot.yourdomain.com` finds the server | `docs/DEPLOY.md` Part 3 |
| [ ] | HTTPS and TLS | Encryption; Cloudflare edge certificate + Cloudflare Origin Certificate on nginx | `docs/DEPLOY.md` Part 3 |
| [ ] | Reverse proxy | nginx receives public traffic and forwards it to the app; WebSocket upgrade headers | `deploy/nginx/lomi-store.conf` |
| [ ] | Logs | `docker compose logs`; never log secrets | `config/settings.py` (`LOGGING`) |
| [ ] | Cron | Scheduled tasks (daily backups) | `docs/DEPLOY.md` Part 6 |

## 9. Engineering habits (what makes code "senior")

| | Habit | Why | See it in |
|---|---|---|---|
| [ ] | Small commits with clear messages | Easy to review and undo | `git log` |
| [ ] | Tests for every rule | Change code without fear | All `tests/` folders |
| [ ] | Fakes instead of real services in tests | Fast, no network, no surprises | `conftest.py` (`FakeBot`) |
| [ ] | Guard clauses | Handle bad cases first; less nesting | `handlers.py` |
| [ ] | Pure functions for logic | Logic without Django or Telegram is easy to test | `catalog/caption.py`, `orders/phone.py` |
| [ ] | Never trust input | Validate captions, phones, button data, the webhook secret | `handlers.py`, `views.py` |
| [ ] | Money as whole numbers | Floats can't store some values exactly | `catalog/models.py` |
| [ ] | Fail safe | One broken update must not stop the bot | `telegram_bot/views.py` |
| [ ] | No secrets in logs or git | Tokens leak through logs and history | `config/settings.py`, `.gitignore` |
| [ ] | Pinned versions, LTS releases | Same result everywhere; long support | `requirements.txt` (Django 5.2 LTS) |

## 10. Next level (not in this project yet)

| | Topic | What it is |
|---|---|---|
| [ ] | Django REST Framework | Build REST APIs (for a future shop page inside Telegram, a mobile app) |
| [ ] | Class-based views | Views as classes; reuse through inheritance |
| [ ] | Celery | Background jobs (e.g. send a reminder an hour later) |
| [ ] | Caching | Save expensive results in Redis |
| [ ] | ruff and mypy | Automatic style and type checking |
| [ ] | GitHub Actions CI | Run tests automatically on every push |
| [ ] | Sentry | Get an alert with the full error when production breaks |
| [ ] | Telegram Mini Apps | A full shop web page that opens inside Telegram |
