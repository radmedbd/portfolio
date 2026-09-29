#!/usr/bin/env bash
set -e
python -m pip install -r requirements.txt
python manage.py makemigrations core
python manage.py migrate
python manage.py seed_demo
echo "Setup complete."
echo "Next: python manage.py createsuperuser"
echo "Then: python manage.py runserver"
