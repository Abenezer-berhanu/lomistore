# Deploying Lomi Store

Do the parts in order. Replace `yourdomain.com` with your real domain everywhere, and `3500` with your real port.

| Part | Where | Time |
|---|---|---|
| 1. BotFather | Telegram app | 5 min |
| 2. Channel and staff group | Telegram app | 5 min |
| 3. Cloudflare DNS | Cloudflare dashboard | 5 min |
| 4. Hetzner server | SSH terminal + Cloudflare dashboard | 30 min |
| 5. Admin and dashboard | Browser | 5 min |
| 6. Day-to-day commands | SSH terminal | |

How it fits together:
```
Customer / Telegram ──HTTPS──> Cloudflare ──HTTPS (port 443)──> [Hetzner: nginx ──> 127.0.0.1:3500 (web)]
                                                                            web ──> db (PostgreSQL), redis
```
- Cloudflare gives the public the HTTPS certificate and hides your server's IP.
- nginx on your server receives the traffic for `bot.yourdomain.com` and passes it to the app. Other sites in nginx are not affected.
- The app port (`3500`) is only open on `127.0.0.1`, so the internet can't reach it directly.

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
3. You'll get its id in Part 4, Step 14.

## Part 3: Cloudflare DNS

### Step 1: Find your server's IP
In the Hetzner console (**console.hetzner.cloud**, then your project, then **Servers**), copy the **IPv4** address of your server. It's the same IP you use with `ssh`.

### Step 2: Add the DNS record
1. Go to **dash.cloudflare.com** and click your domain.
2. Left menu: **DNS**, then **Records**, then **Add record**.
3. Fill in:
   - Type: `A`
   - Name: `bot`
   - IPv4 address: your server IP
   - Proxy status: **Proxied** (orange cloud ON)
   - TTL: `Auto`
4. **Save**. If a `bot` record already exists, edit it instead of adding a second one.

### Step 3: HTTPS settings
1. Left menu: **SSL/TLS**, then **Edge Certificates**. Turn **Always Use HTTPS** on.
2. Left menu: **SSL/TLS**, then **Overview**. Only **look** at the current mode for now (Off, Flexible, Full, or Full (strict)) and write it down. You change it in Part 4, Step 11, after the server is ready.

### Step 4: WebSockets and bots
1. Left menu: **Network**. Check that **WebSockets** is **On** (the live dashboard needs it).
2. Left menu: **Security**, then **Bots** (in the newer dashboard: **Security**, then **Settings**, then filter by **Bot traffic**). Check that **Bot Fight Mode** is **Off**. When it's on, Cloudflare can block Telegram's messages to your bot.

Cloudflare sometimes renames menus. If you can't find something, use the search box at the top of the dashboard.

## Part 4: Hetzner server

All commands below are typed on the server, logged in as `root`.

### Step 1: Connect
On your laptop, in PowerShell:
```powershell
ssh root@YOUR_SERVER_IP
```

### Step 2: Find a free port for the app
See every port in use, and which program uses it:
```bash
ss -tlnp
docker ps --format 'table {{.Names}}\t{{.Ports}}'
```
Find the highest port your projects use and the next round hundred after it. If the highest is 3401, this prints 3500:
```bash
LAST=$(ss -tlnH | awk '{print $4}' | awk -F: '{print $NF}' | sort -n | uniq | awk '$1 < 10000' | tail -1)
echo "highest used: $LAST   ->   use: $(( (LAST / 100 + 1) * 100 ))"
```
(Ports of 10000 and above are skipped, because those are usually random temporary ports.)

Double-check that the port you chose is free. This must print **nothing**:
```bash
ss -tln | grep ':3500 '
```
Write the port down for `APP_PORT`. It's only open on `127.0.0.1` (the server itself), so you don't change any firewall for it.

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
```
Leave `TELEGRAM_ADMIN_CHAT_ID` empty for now. Save with `Ctrl+O`, `Enter`, then exit with `Ctrl+X`. Then lock the file so only root can read it:
```bash
chmod 600 .env
```

### Step 6: Start the app
```bash
docker compose up -d --build
docker compose ps
```
The three services (`web`, `db`, `redis`) should say `running` (db says `healthy`). The first build takes a few minutes.

Check the app on the server itself. It must print `ok`:
```bash
curl http://127.0.0.1:3500/health/
```
If it fails, read the logs (press `Ctrl+C` to stop following them):
```bash
docker compose logs -f web
```

### Step 7: See what's using ports 80 and 443
```bash
ss -tlnp | grep -E ':(80|443) '
```
Look at the program name in `users:(("...`:

| What you see | What it means | What to do |
|---|---|---|
| `nginx` | nginx already serves your other sites | Skip Step 8, go to Step 9 |
| Nothing printed | No web server yet | Do Step 8 |
| `caddy`, `apache2`, `traefik`, or `docker-proxy` | A different web server | Stop and send me the output. The setup is different. |

### Step 8: Install nginx and open port 443 (only if nothing was printed in Step 7)
```bash
apt update && apt install -y nginx
systemctl enable --now nginx
```
Check the server firewall:
```bash
ufw status
```
If it says `Status: active`, open HTTPS:
```bash
ufw allow 443/tcp
```
If it says `inactive`, do nothing.

Also check the **Hetzner Cloud firewall**: Hetzner console, then **Firewalls**. If a firewall is attached to your server, it needs an inbound rule for **TCP port 443** (source: Any IPv4, Any IPv6). If the Firewalls page is empty, do nothing.

### Step 9: Cloudflare Origin Certificate (free, valid for 15 years)
This certificate is what nginx shows to Cloudflare. Create it in Cloudflare and paste it **straight into the server**. Cloudflare shows the private key **only once**.

1. In Cloudflare: your domain, then **SSL/TLS**, then **Origin Server**, then **Create Certificate**.
2. Keep the defaults: **Generate private key and CSR with Cloudflare**, key type **RSA (2048)**, hostnames `*.yourdomain.com` and `yourdomain.com`, validity **15 years**. Click **Create**.
3. You now see two boxes: **Origin Certificate** and **Private Key** (format PEM). Keep this page open.
4. On the server, make a folder and paste the certificate:
   ```bash
   mkdir -p /etc/ssl/cloudflare
   nano /etc/ssl/cloudflare/lomi-store.pem
   ```
   Copy the whole **Origin Certificate** box (from `-----BEGIN CERTIFICATE-----` to `-----END CERTIFICATE-----`), paste it in nano with a **right-click**, then save with `Ctrl+O`, `Enter`, `Ctrl+X`.
5. Paste the key the same way:
   ```bash
   nano /etc/ssl/cloudflare/lomi-store.key
   ```
   Copy the whole **Private Key** box (from `-----BEGIN PRIVATE KEY-----` to `-----END PRIVATE KEY-----`), paste, save.
6. Lock the key:
   ```bash
   chmod 600 /etc/ssl/cloudflare/lomi-store.key
   ```
7. Now click **OK** in Cloudflare. If you lose the key later, revoke the certificate on the same page and create a new one.

### Step 10: Add the site to nginx
The ready-made config is in the project at `deploy/nginx/lomi-store.conf`. These commands copy it with your domain and port filled in:
```bash
cd /opt/lomi-store
DOMAIN=bot.yourdomain.com
PORT=3500
ls /etc/nginx/sites-enabled
```
- If `ls` shows a list of files (or nothing, but no error), use:
  ```bash
  sed -e "s/bot.yourdomain.com/$DOMAIN/g" -e "s/127.0.0.1:3500/127.0.0.1:$PORT/g" deploy/nginx/lomi-store.conf > /etc/nginx/sites-available/lomi-store
  ln -s /etc/nginx/sites-available/lomi-store /etc/nginx/sites-enabled/lomi-store
  ```
- If `ls` says `No such file or directory`, your nginx uses `conf.d` instead:
  ```bash
  sed -e "s/bot.yourdomain.com/$DOMAIN/g" -e "s/127.0.0.1:3500/127.0.0.1:$PORT/g" deploy/nginx/lomi-store.conf > /etc/nginx/conf.d/lomi-store.conf
  ```

Test the config, then load it. `nginx -t` must say `syntax is ok` and `test is successful`. **Only reload if it does**, so your other sites never go down:
```bash
nginx -t && systemctl reload nginx
```
Test nginx on the server, without Cloudflare. It must print `ok`:
```bash
curl -k --resolve $DOMAIN:443:127.0.0.1 https://$DOMAIN/health/
```
(`-k` is needed here only because the origin certificate is trusted by Cloudflare, not by curl.)

### Step 11: Set Cloudflare SSL mode to Full (strict)
This makes the connection between Cloudflare and your server encrypted and checked.

**If `bot.yourdomain.com` is the only site on this domain**, or the mode you wrote down in Part 3 was already **Full (strict)**:
1. Cloudflare: your domain, then **SSL/TLS**, then **Overview**.
2. Click **Configure**, choose **Custom SSL/TLS**, select **Full (strict)**, and **Save**.

**If other websites already use this domain** (for example `yourdomain.com` itself or `www`) and the mode was something else, don't change the global mode, because it can break those sites. Set it only for the bot:
1. Cloudflare: your domain, then **Rules**, then **Configuration Rules** (or **Rules > Overview > Create rule > Configuration Rule**).
2. Rule name: `lomi-store ssl`.
3. **Custom filter expression**: Field `Hostname`, Operator `equals`, Value `bot.yourdomain.com`.
4. Scroll to **SSL**, click **Add**, choose **Full (strict)**.
5. **Deploy**.

Now test through Cloudflare, from the server and from your laptop's browser. Both must show `ok`:
```bash
curl https://bot.yourdomain.com/health/
```
Browser: `https://bot.yourdomain.com/health/`

### Step 12: Create your admin login
```bash
cd /opt/lomi-store
docker compose exec web python manage.py createsuperuser
```
It asks for a username, email (you can leave it empty), and password (typing is invisible, that's normal).

### Step 13: Connect the bot to the server
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
The last line is expected right now. Step 14 fixes it.

### Step 14: Staff group id
1. In the staff group, send `/chatid@lomistore_bot` (use your bot's username).
2. The bot answers `This chat id is -100...`.
3. Put that number in `.env` as `TELEGRAM_ADMIN_CHAT_ID`, then restart:
```bash
nano .env
docker compose up -d
docker compose exec web python manage.py telegram_setup
```
Now every line should start with `OK`.

### Step 15: Test the whole flow
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

Log in with the user from Part 4, Step 12.

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
| nginx error log | `tail -50 /var/log/nginx/error.log` |

**Daily automatic backup** at 03:00. Run `crontab -e` and add this line:
```
0 3 * * * cd /opt/lomi-store && docker compose exec -T db pg_dump -U lomi lomi | gzip > /root/backups/lomi-$(date +\%F).sql.gz
```
Copy backups off the server now and then (Hetzner Storage Box, or `scp` to your laptop).

## Troubleshooting

| Problem | Fix |
|---|---|
| No Order button under a post | Run `telegram_setup`. Check the bot has **Edit Messages of Others**. One photo only, no albums. Check the staff group for a "was not added" message. |
| `nginx -t` fails with `[::]:443` / address family error | Your server has no IPv6. Delete the line `listen [::]:443 ssl;` from the config and run `nginx -t` again. |
| `nginx -t` fails with `cannot load certificate` | The `.pem` or `.key` file is wrong or empty. Paste them again (Step 9), including the BEGIN and END lines. |
| Cloudflare error **521** or **522** | Cloudflare can't reach port 443. Check `systemctl status nginx`, `ufw status`, and the Hetzner Cloud firewall (Step 8). |
| Cloudflare error **525** | nginx isn't serving HTTPS for this name. Check that `server_name` in the config is exactly `bot.yourdomain.com`, then `nginx -t && systemctl reload nginx`. |
| Cloudflare error **526** | The certificate on the server isn't the Cloudflare Origin Certificate, or it doesn't cover `bot.yourdomain.com`. Redo Step 9. |
| **502 Bad Gateway** (nginx page) | The app isn't running or the port in the nginx config is wrong. Check `docker compose ps` and `curl http://127.0.0.1:3500/health/`. |
| Too many redirects | The SSL mode is **Flexible**. Set **Full (strict)** (Step 11). |
| `telegram_setup` shows a last webhook error with **403** | Cloudflare is blocking Telegram. Turn **Bot Fight Mode** off (Part 3, Step 4) and look at **Security > Events** for what blocked it. If it's a 403 from Django instead, `TELEGRAM_WEBHOOK_SECRET` changed: run `telegram_setup` again. |
| "CSRF verification failed" on admin login | `PUBLIC_BASE_URL` must be exactly `https://bot.yourdomain.com` (https, no slash at the end). Then run `docker compose up -d`. |
| "Bad Request (400)" page | Add the domain to `DJANGO_ALLOWED_HOSTS`, then `docker compose up -d`. |
| Dashboard stuck on "Reconnecting" | Check `docker compose ps` (is redis running?). In Cloudflare, under **Network**, check that **WebSockets** is on. Check that the nginx config has the `location /ws/` block. |
| Customers say the bot doesn't answer | Run `telegram_setup` and read any "last webhook error" line, then check `docker compose logs -f web`. |
| The staff group was upgraded (Telegram changes its id) | Send `/chatid@yourbot` again and update `.env`. |
