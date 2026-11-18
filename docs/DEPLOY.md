# Deploying Lomi Store

Do the parts in order. Replace `yourdomain.com` with your real domain everywhere.

| Part | Where | Time |
|---|---|---|
| 1. BotFather | Telegram app | 5 min |
| 2. Channel and staff group | Telegram app | 5 min |
| 3. Cloudflare Tunnel | Cloudflare dashboard | 10 min |
| 4. Hetzner server | SSH terminal | 20 min |
| 5. Admin and dashboard | Browser | 5 min |
| 6. Day-to-day commands | SSH terminal | |

How it fits together:
```
Customer / Telegram ──HTTPS──> Cloudflare ──tunnel──> [Hetzner: tunnel container ─> web:8000]
                                                               web ─> db (PostgreSQL), redis
```
The tunnel is an outgoing connection from your server to Cloudflare. That means **no ports are opened** and **nothing changes for your other projects** (their nginx/caddy, ports 80/443 stay untouched).

---

## Part 1: BotFather (create the bot)

1. In Telegram, search **@BotFather** (it has a blue check mark) and press **Start**.
2. Send `/newbot`.
3. It asks for a **name**: send `Lomi Store`.
4. It asks for a **username**: it must end in `bot`. Try `lomistore_bot`. If it's taken, try `lomi_store_et_bot` or similar.
5. BotFather replies with a **token** like `7123456789:AAH...`. This is the bot's password.
   - Save it for `TELEGRAM_BOT_TOKEN`.
   - Save the username (without @) for `TELEGRAM_BOT_USERNAME`.
   - Never share it. If it leaks: `/revoke` in BotFather, then update `.env`.
6. Make it look nice (optional but recommended):
   - `/setdescription`, choose your bot, send: `Order from Lomi Store. Tap "Order now" under any item in our channel and we will call you.`
   - `/setabouttext`: `Lomi Store, order online and we call you.`
   - `/setuserpic`: send your logo.
7. Leave the other settings as they are (group joining allowed, privacy mode on).

## Part 2: Channel and staff group

**Public channel** (skip creating it if you already have one):
1. Telegram: **New Channel**, name `Lomi Store`, choose **Public**, pick the link, e.g. `t.me/lomistore`.
2. The part after `t.me/` is `TELEGRAM_CHANNEL_USERNAME` (e.g. `lomistore`).

**Make the bot a channel admin** (required, it adds the Order buttons):
1. Open the channel, then **Administrators**, then **Add Admin**, and search your bot's username.
2. Turn on **Post Messages** and **Edit Messages of Others**. The second one is required.
3. Save.

**Staff group** (where new orders arrive):
1. Create a **private group**, e.g. `Lomi Store Staff`.
2. Add your staff and the bot.
3. You'll get its id in Part 4, step 9.

## Part 3: Cloudflare Tunnel

1. Go to **dash.cloudflare.com**, and in the left menu open **Zero Trust**.
   - First time only: choose a team name and the **Free** plan.
   - If Cloudflare insists on a payment card for the free plan and you can't add one, stop here and tell me. There's a plan B.
2. Go to **Networks**, then **Tunnels**, then **Create a tunnel**, and choose **Cloudflared**.
3. Name it `lomi-store` and save.
4. On the install screen choose **Docker**. It shows a command like:
   `docker run cloudflare/cloudflared:latest tunnel --no-autoupdate run --token eyJhIjoi...`
   **Don't run it.** Copy only the long text after `--token`. That's `CLOUDFLARE_TUNNEL_TOKEN`.
5. Click **Next** to reach **Public Hostname** (sometimes called "Route traffic"), and fill in:
   - Subdomain: `bot`
   - Domain: `yourdomain.com`
   - Path: leave empty
   - Service type: `HTTP`
   - URL: `web:8000`
6. Save. Cloudflare creates the `bot.yourdomain.com` DNS record by itself.
   - If it complains that a record already exists, delete the old `bot` record under **DNS** first.
7. On your domain (the normal dashboard, not Zero Trust), go to **SSL/TLS**, then **Edge Certificates**, and turn **Always Use HTTPS** on.

Cloudflare sometimes renames menus. If you can't find **Networks > Tunnels**, look for **Networking > Tunnels**.

## Part 4: Hetzner server

### Step 1: Connect
```bash
ssh root@YOUR_SERVER_IP
```

### Step 2: Find a free port
See every port in use, and which program uses it:
```bash
sudo ss -tlnp
docker ps --format 'table {{.Names}}\t{{.Ports}}'
```
Find the highest port your projects use and the next round hundred after it. If the highest is 3401, this prints 3500:
```bash
LAST=$(sudo ss -tlnH | awk '{print $4}' | awk -F: '{print $NF}' | sort -n | uniq | awk '$1 < 10000' | tail -1)
echo "highest used: $LAST   ->   use: $(( (LAST / 100 + 1) * 100 ))"
```
(Ports of 10000 and above are skipped, because those are usually random temporary ports.)

Double-check that the port you chose is free. This must print **nothing**:
```bash
sudo ss -tln | grep ':3500 '
```
Write the port down for `APP_PORT`. It's only reachable from the server itself (`127.0.0.1`), so there's no firewall change.

### Step 3: Docker
```bash
docker --version
docker compose version
```
If either one fails, install Docker:
```bash
curl -fsSL https://get.docker.com | sh
```

### Step 4: Get the code onto the server

**Option A: GitHub (recommended, makes updates easy)**

On your **laptop**, create an empty **private** repository on github.com called `lomi-store` (no README). Then in the project folder:
```powershell
git remote add origin https://github.com/YOUR_GITHUB_NAME/lomi-store.git
git push -u origin master
```
On the **server**:
```bash
cd /opt
git clone https://github.com/YOUR_GITHUB_NAME/lomi-store.git
cd lomi-store
```
Because the repository is private, git asks for a username and password. For the password, use a GitHub **personal access token** (GitHub > Settings > Developer settings > Personal access tokens > Fine-grained, with read access to this one repo).

**Option B: copy a file (no GitHub)**

On your **laptop**, in the project folder:
```powershell
git archive -o lomi.tar.gz HEAD
scp lomi.tar.gz root@YOUR_SERVER_IP:/opt/
```
On the **server**:
```bash
mkdir -p /opt/lomi-store && tar -xzf /opt/lomi.tar.gz -C /opt/lomi-store && cd /opt/lomi-store
```

### Step 5: Create the `.env` file
```bash
cp .env.example .env
python3 -c "import secrets; print(secrets.token_urlsafe(50))"   # use for DJANGO_SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(24))"       # use for POSTGRES_PASSWORD
python3 -c "import secrets; print(secrets.token_urlsafe(32))"   # use for TELEGRAM_WEBHOOK_SECRET
nano .env
```
Fill it like this (your values):
```ini
DJANGO_SECRET_KEY=<first generated value>
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=bot.yourdomain.com,localhost,127.0.0.1
PUBLIC_BASE_URL=https://bot.yourdomain.com
APP_PORT=3500
POSTGRES_PASSWORD=<second generated value>
TELEGRAM_BOT_TOKEN=<from BotFather>
TELEGRAM_BOT_USERNAME=lomistore_bot
TELEGRAM_WEBHOOK_SECRET=<third generated value>
TELEGRAM_CHANNEL_USERNAME=lomistore
TELEGRAM_ADMIN_CHAT_ID=
CLOUDFLARE_TUNNEL_TOKEN=<from Cloudflare>
```
Leave `TELEGRAM_ADMIN_CHAT_ID` empty for now. Save with `Ctrl+O`, `Enter`, then exit with `Ctrl+X`. Then lock the file so only root can read it:
```bash
chmod 600 .env
```

### Step 6: Start everything
```bash
docker compose up -d --build
docker compose ps
```
All four services (`web`, `db`, `redis`, `tunnel`) should say `running` (db says `healthy`). The first build takes a few minutes.

Check that it works, first on the server and then through Cloudflare. Both must print `ok`:
```bash
curl http://127.0.0.1:3500/health/
curl https://bot.yourdomain.com/health/
```
If something fails, read the logs (press `Ctrl+C` to stop following them):
```bash
docker compose logs -f web
docker compose logs --tail 50 tunnel
```

### Step 7: Create your admin login
```bash
docker compose exec web python manage.py createsuperuser
```

### Step 8: Connect the bot to the server
```bash
docker compose exec web python manage.py telegram_setup
```
Expected output:
```
OK    Bot found: @lomistore_bot
OK    Webhook set to https://bot.yourdomain.com/telegram/webhook/
OK    The bot is an admin of @lomistore and can add Order buttons
CHECK TELEGRAM_ADMIN_CHAT_ID is empty: staff won't get order messages. ...
```
The last line is expected right now. Step 9 fixes it.

### Step 9: Staff group id
1. In the staff group, send `/chatid@lomistore_bot` (use your bot's username).
2. The bot answers `This chat id is -100...`.
3. Put that number in `.env` as `TELEGRAM_ADMIN_CHAT_ID`, then restart:
```bash
nano .env
docker compose up -d
docker compose exec web python manage.py telegram_setup
```
Now every line should start with `OK`.

### Step 10: Test the whole flow
1. Post **one photo** in the channel with this caption:
   ```
   Nike Air Force 1 White
   Price: 3,500 ETB
   Sizes: 40, 41, 42-44
   Original, made in Vietnam
   ```
2. Within a second or two, an **Order now** button appears under the post.
3. Tap it, tap **Start** in the bot, pick a size, and share your phone number.
4. The staff group gets the order, and the dashboard shows it instantly.

## Part 5: Admin and live dashboard

| Page | Address | What for |
|---|---|---|
| Live dashboard | `https://bot.yourdomain.com/dashboard/` | Keep it open on a staff phone or PC. Click **Turn on sound** once. New orders appear instantly with a beep. |
| Admin | `https://bot.yourdomain.com/admin/` | Change order status, add notes (address, delivery day), search by phone, mark products sold out. |

Log in with the user from Step 7.

**Add staff accounts** (don't share your own login):
1. Go to Admin, then **Users**, then **Add user**. Set a username and password, and save.
2. Tick **Staff status**. Do NOT tick Superuser status.
3. Under **User permissions**, add:
   - `orders | order | Can view order` and `Can change order`
   - `orders | customer | Can view customer`
   - `catalog | product | Can view product` and `Can change product`
4. Save. The staff member can now log in to the admin and the dashboard.

**Rules for staff posting in the channel:**
- One photo per post. Albums (several photos at once) can't have an Order button.
- Line 1 is the product name. Then `Price: ...` and `Sizes: ...`. Any other lines become the description.
- Sold out: edit the post and add a line `SOLD OUT`, or untick it in Admin > Products. **Deleting a post does not remove the product** (Telegram doesn't tell bots about deletions), so mark it sold out in Admin.
- If a caption is wrong, the bot tells the staff group why. Edit the post and it's picked up again.

## Part 6: Day-to-day commands

Run these on the server, inside `/opt/lomi-store`.

| Task | Command |
|---|---|
| See status | `docker compose ps` |
| Follow app logs | `docker compose logs -f web` |
| Restart the app | `docker compose restart web` |
| Update after new code (Option A) | `git pull && docker compose up -d --build` |
| Stop everything | `docker compose down` (your data stays in the `lomi_store_postgres_data` volume) |
| Back up the database now | `mkdir -p /root/backups && docker compose exec -T db pg_dump -U lomi lomi \| gzip > /root/backups/lomi-$(date +%F).sql.gz` |

**Daily automatic backup** at 03:00. Run `crontab -e` and add this line:
```
0 3 * * * cd /opt/lomi-store && docker compose exec -T db pg_dump -U lomi lomi | gzip > /root/backups/lomi-$(date +\%F).sql.gz
```
Copy backups off the server now and then (Hetzner Storage Box, or `scp` to your laptop).

## Troubleshooting

| Problem | Fix |
|---|---|
| No Order button under a post | Run `telegram_setup`. Check the bot has **Edit Messages of Others**. One photo only, no albums. Check the staff group for a "was not added" message. |
| `https://bot.yourdomain.com` shows Cloudflare error 1033 or 502 | Run `docker compose logs --tail 50 tunnel`. Check the token in `.env`, and that the hostname URL in Cloudflare is exactly `web:8000`. |
| "CSRF verification failed" on admin login | `PUBLIC_BASE_URL` must be exactly `https://bot.yourdomain.com` (https, no slash at the end). Then run `docker compose up -d`. |
| "Bad Request (400)" page | Add the domain to `DJANGO_ALLOWED_HOSTS`, then `docker compose up -d`. |
| Dashboard stuck on "Reconnecting" | Check `docker compose ps` (is redis running?). In Cloudflare, under **Network**, check that **WebSockets** is on. |
| Customers say the bot doesn't answer | Run `telegram_setup` and read any "last webhook error" line, then check `docker compose logs -f web`. |
| The staff group was upgraded (Telegram changes its id) | Send `/chatid@yourbot` again and update `.env`. |
