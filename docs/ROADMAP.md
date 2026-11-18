# Lomi Store: Roadmap

A Telegram shop for the Ethiopian market. It starts with shoes and has a general name, so other products can come later.
This is a real production project **and** a Python + Django learning path.

---

## 1. How the shop works

```
Staff post a photo + caption in the public channel
        │
        ▼
Bot (an admin of the channel) receives the post
   ├─ reads the caption: name, price, sizes
   ├─ saves the product in the database (with the Telegram photo file_id)
   └─ adds a [ Order ] button to the post
        │  customer taps Order
        ▼
Bot opens in a private chat
   ├─ shows the same product
   ├─ customer picks a size (buttons)
   ├─ customer shares a phone number
   └─ "Thank you! Lomi Store will call you soon."
        │
        ▼
Staff are notified
   ├─ private Telegram admin group (message with all order details)
   └─ live staff dashboard in the browser (WebSocket, no refresh needed)
        │
        ▼
Staff call the customer and update the order status in Django Admin
```

### Decisions made

| Topic | Decision |
|---|---|
| Images | Stay on Telegram. The database stores only the photo `file_id`. No storage bill. |
| Catalog | The public channel. One post = one product. |
| Posting | Staff post straight to the channel. The bot picks the post up instantly. |
| Language | English |
| Size | The bot always asks for the size. |
| Phone | Accepted from the "Share phone" button, a contact card, or typed. The bot checks whether the number belongs to the customer's own Telegram account but **never refuses**. It only marks the order: `phone_is_own = False`. |
| Sold out | Edit the caption (add `SOLD OUT`) or switch it off in Django Admin. Telegram does **not** tell bots when a post is deleted. |
| Staff dashboard | Django Admin plus a live orders page using WebSockets (Django Channels) |
| Server | Your Hetzner VPS |
| Domain | On Cloudflare. The bot will live at `bot.<yourdomain>` |

### Caption format staff must follow

```
Nike Air Force 1 White
Price: 3,500 ETB
Sizes: 40, 41, 42, 43
Any extra lines become the description.
```

If the bot can't read a caption, it messages the admin group so staff can fix it.

### Main data (preview, built in Phase 2)

- **Product**: channel message id, photo file_id, name, price, sizes, description, sold out, created at
- **Customer**: Telegram user id, name, username, saved phone
- **Order**: customer, product, size, phone, phone_is_own, status (new, called, confirmed, delivered, cancelled), created at

---

## 2. Phases

Each phase has its own file in `docs/`. A phase file is written when we reach it, so it fits what you learned in the previous phases.

| # | Phase | What we build | What you learn |
|---|---|---|---|
| 0 | [Python foundations](phase-00-python.md) | Caption parser with tests | Packages, constants, regex, custom exceptions, dataclasses, type hints, comprehensions, walrus, `match`, pytest fixtures and parametrize |
| 1 | Telegram with plain Python | Script that calls the Bot API directly | HTTP with `httpx`, JSON, environment variables, how the Bot API works with no library hiding it |
| 2 | Django fundamentals | Django project, models, admin | Project vs app, settings, URLs, views, models, ORM, migrations, Django Admin, Django shell |
| 3 | Webhook + product import | Channel post becomes a product, bot adds the Order button | Webhooks, CSRF, secret header check, Cloudflare Tunnel, management commands, handling edited posts |
| 4 | Order flow | Deep link, size, phone, confirmation, admin group alert | Per-customer conversation state, inline keyboards, callback queries, phone normalizing (09.., 07.., +251..), DB transactions |
| 5 | Staff operations | Order statuses, staff accounts, sold-out switch | Admin customization, users, groups, permissions, signals, status rules |
| 6 | Testing and code quality | Full test suite, automatic checks | pytest-django, factories, mocking Telegram, fixtures, coverage, ruff, pre-commit, GitHub Actions CI |
| 7 | Reliability | Fast webhook, retries, no duplicate orders | Celery + Redis background jobs, idempotency, Telegram rate limits, logging, Sentry |
| 8 | Live staff dashboard | New orders appear instantly with a sound | WebSockets, ASGI, Django Channels, Redis channel layer, consumers, groups, auth on WebSockets |
| 9 | Production setup | Docker setup with PostgreSQL | Docker, docker compose, PostgreSQL, ASGI server (uvicorn), static files, dev vs prod settings, security checks |
| 10 | Deployment on Hetzner | Live at `bot.<yourdomain>` | Linux, SSH, firewall, Cloudflare DNS + SSL, Caddy reverse proxy, backups, auto-deploy from GitHub |
| 11 | Growth (advanced) | REST API for a future shop page inside Telegram, sales stats | Django REST Framework, caching, async views, query optimization, analytics queries |
| 12 | Capstone | A different small Django project built alone from an empty folder | Proof that you can do it yourself. I only review. |

The shop can take real orders after **Phase 5**. Phases 6 to 10 make it production-grade.

---

## 3. How we work

1. **I build one whole phase**: code, tests, and the tests passing.
2. **The code teaches.** Important lines have short comments:
   - `LEARN:` what the feature is
   - `SENIOR:` why a professional writes it this way
   - `BEGINNER:` the simpler way, when there is one
   - `WHY NOT:` why we don't use the beginner way
3. **I commit the phase** before starting the next one. The start of a new phase never has uncommitted work.
4. **The phase file is a reading guide**: which file to open, which lines to read in which order, what to focus on, commands to run, and the output to expect.
5. **You read, run and ask.** Ask about anything unclear. When you're ready, say "next phase".
6. **Later phases** have small "change this yourself" exercises, so reading turns into writing. The Capstone (Phase 12) is all you.

---

## 4. Progress

- [x] Phase 0: Python foundations (caption parser, 37 tests)
- [ ] Phase 1: Telegram with plain Python
- [ ] Phase 2: Django fundamentals
- [ ] Phase 3: Webhook + product import
- [ ] Phase 4: Order flow
- [ ] Phase 5: Staff operations
- [ ] Phase 6: Testing and code quality
- [ ] Phase 7: Reliability
- [ ] Phase 8: Live staff dashboard (WebSockets)
- [ ] Phase 9: Production setup
- [ ] Phase 10: Deployment on Hetzner
- [ ] Phase 11: Growth
- [ ] Phase 12: Capstone
