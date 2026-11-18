FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install packages first: Docker reuses this layer until requirements.txt changes.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Collect admin CSS/JS into /app/staticfiles. The key is only for this build step.
RUN DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput

# Don't run as root inside the container.
RUN useradd --system --no-create-home app
USER app

EXPOSE 8000

# Apply database changes, then start the ASGI server (HTTP + WebSockets).
CMD ["sh", "-c", "python manage.py migrate --noinput && exec daphne -b 0.0.0.0 -p 8000 --proxy-headers config.asgi:application"]
