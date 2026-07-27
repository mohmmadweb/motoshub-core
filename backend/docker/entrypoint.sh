#!/usr/bin/env bash
# Dispatch by first arg: web | worker | beat | migrate | seed | shell
set -e

case "${1:-web}" in
  web)
    python manage.py migrate --noinput
    python manage.py seed_rbac
    python manage.py seed_demo || true
    exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile -
    ;;
  worker)
    exec celery -A config worker -l info
    ;;
  beat)
    exec celery -A config beat -l info
    ;;
  migrate)
    exec python manage.py migrate --noinput
    ;;
  seed)
    python manage.py seed_rbac && exec python manage.py seed_demo
    ;;
  *)
    exec "$@"
    ;;
esac
