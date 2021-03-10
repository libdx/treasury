#!/bin/sh

echo "Waiting for PostgreSQL..."

while ! nc -z web-db 5432; do
    sleep 0.1
done

echo "PostgreSQL started"

python manage.py runserver 0.0.0.0:8000

