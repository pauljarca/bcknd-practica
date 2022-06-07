#!/bin/sh

if [ $# -eq 0 ]
then
    set -ex

    python manage.py collectstatic --no-input --verbosity 0
    python manage.py migrate --no-input
    python manage.py generateimages

    python manage.py shell -c "import setsitename"

    chmod -R u=rwX,g=rX,o= /app/*
    chown -RL root:101 /app/staticfiles /app/server/
    chown -RL django:101 /app/server/logs/ /app/media/
    find /app/ -type d -exec chmod g+s {} +

    PORT=8000 su-exec django gunicorn practica.wsgi --timeout 180 --log-file -
else
    exec python manage.py "$@"
fi
