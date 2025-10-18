#!/usr/bin/env bash
set -e

# ── Helper: изчакай Postgres (ако DB_HOST е зададен) ────────────────────────────
wait_for_db() {
  if [ -n "$DB_HOST" ]; then
    echo "⏳ Waiting for DB $DB_HOST:${DB_PORT:-5432} ..."
    python - <<'PY'
import os, socket, time
host=os.getenv("DB_HOST",""); port=int(os.getenv("DB_PORT","5432"))
if host:
    s=socket.socket()
    while s.connect_ex((host,port))!=0:
        time.sleep(1)
    s.close()
print("✅ DB is reachable.")
PY
  fi
}

migrate() {
  wait_for_db
  echo "➡️ migrate"
  python manage.py migrate --noinput
}

collectstatic() {
  echo "➡️ collectstatic"
  python manage.py collectstatic --noinput || true
}

# ── Ensure superuser (идемпотентно, ПРЕЗ manage.py) ────────────────────────────
create_superuser() {
  if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "➡️ ensure superuser (idempotent)"

    # 1) Опитай да създадеш; ако вече съществува – продължаваме
    python manage.py createsuperuser \
      --noinput \
      --username "${DJANGO_SUPERUSER_USERNAME:-admin}" \
      --email "${DJANGO_SUPERUSER_EMAIL}" || true

    # 2) Гарантирай паролата (и по email, и по username за съвместимост)
    python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
U = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
username = os.environ.get('DJANGO_SUPERUSER_USERNAME','admin')
pwd = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

u = U.objects.filter(email=email).first() or U.objects.filter(username=username).first()
if not u:
    # последен опит – ако custom user иска конкретни полета
    try:
        u = U.objects.create_superuser(username=username, email=email, password=pwd)
    except TypeError:
        u = U.objects.create_superuser(email=email, password=pwd)
    print('✅ Superuser created:', u)
else:
    u.set_password(pwd); u.save()
    print('✅ Superuser ensured:', u)
"
  else
    echo "⚠️ Skip superuser (DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_PASSWORD not set)"
  fi
}

case "$1" in
  web)
    migrate
    collectstatic
    create_superuser
    echo "🚀 starting gunicorn"
    exec gunicorn todo_list_backend.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers "${GUNICORN_WORKERS:-3}" \
      --timeout "${GUNICORN_TIMEOUT:-120}"
    ;;
  migrate)
    migrate
    ;;
  collectstatic)
    collectstatic
    ;;
  shell)
    exec python manage.py shell
    ;;
  manage)
    shift
    exec python manage.py "$@"
    ;;
  *)
    echo "Usage: $0 {web|migrate|collectstatic|shell|manage ...}"
    exit 1
    ;;
esac
