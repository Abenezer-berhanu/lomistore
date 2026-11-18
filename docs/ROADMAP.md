# Lomi Store: overview

A Telegram shop for the Ethiopian market. It starts with shoes and has a general name, so other products can come later.

**Status: built and ready to deploy.** Follow [DEPLOY.md](DEPLOY.md). To learn how it works, use [LEARNING.md](LEARNING.md).

## How the shop works

```
Staff post one photo + caption in the public channel
        │
        ▼
Bot (an admin of the channel) receives the post
   ├─ reads the caption: name, price, sizes
   ├─ saves the product (the photo stays on Telegram, we keep its file_id)
   └─ adds an [ Order now ] button under the post
        │  customer taps Order now
        ▼
Bot opens in a private chat
   ├─ shows the product with size buttons
   ├─ customer picks a size
   ├─ customer shares their phone, sends a contact card, or types a number
   └─ "Thank you! Lomi Store will call you soon."
        │
        ▼
Staff are notified
   ├─ message in the private staff group
   └─ live dashboard in the browser (WebSocket, instant, with sound)
        │
        ▼
Staff call the customer and update the status in Django Admin
```

## Decisions

| Topic | Decision |
|---|---|
| Images | Stay on Telegram. Only the photo `file_id` is stored. No storage bill. |
| Catalog | The public channel. One post = one product. |
| Language | English |
| Size | Always asked |
| Phone | Accepted from the share button, a contact card, or typed. Never refused. The order is marked when the number isn't the customer's own Telegram number. |
| Sold out | Add `SOLD OUT` to the caption, or untick it in Admin. Deleting a post doesn't remove the product. |
| Stack | Django 5.2 LTS, Channels (WebSockets), PostgreSQL, Redis, Daphne (ASGI server) |
| Hosting | Hetzner VPS with Docker Compose, behind nginx, at `bot.<yourdomain>` (Cloudflare DNS, proxied) |

## Code map

| Folder | What's inside |
|---|---|
| `config/` | Settings, URLs, ASGI entry point (HTTP + WebSocket routing) |
| `catalog/` | `Product` model, caption parser, product admin |
| `orders/` | `Customer` and `Order` models, phone normalizing, admin, live dashboard (view, template, WebSocket consumer) |
| `telegram_bot/` | Telegram API client, webhook view, the conversation logic (`handlers.py`), the `telegram_setup` command |
| `conftest.py` | Test helpers: a fake bot and Telegram update builders |
| `Dockerfile`, `compose.yaml` | Production containers |
| `deploy/nginx/` | nginx site config for the server |

## Phase 0 reading guide

[phase-00-python.md](phase-00-python.md) is a line-by-line guide to `catalog/caption.py`, where every line is explained with `LEARN` / `SENIOR` / `BEGINNER` / `WHY NOT` comments. It's a good first file to study.
