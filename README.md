# Lomi Store

Telegram channel shop: staff post products in a public channel, customers tap **Order now**, pick a size, share a phone number, and staff call them.

- How it works and code map: [docs/ROADMAP.md](docs/ROADMAP.md)
- Deploy to the server: [docs/DEPLOY.md](docs/DEPLOY.md)
- Topics to learn from this code: [docs/LEARNING.md](docs/LEARNING.md)

## Run on your laptop (Windows PowerShell)

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt

$env:DJANGO_DEBUG = "1"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/dashboard/ and log in. The bot itself needs HTTPS, so it only works once it's deployed.

## Tests

```powershell
pytest
```
