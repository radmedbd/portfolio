$ErrorActionPreference = "Stop"

Write-Host "Installing dependencies..." -ForegroundColor Cyan
python -m pip install -r requirements.txt

Write-Host "Creating migrations..." -ForegroundColor Cyan
python manage.py makemigrations core

Write-Host "Applying migrations..." -ForegroundColor Cyan
python manage.py migrate

Write-Host "Creating editable demo content..." -ForegroundColor Cyan
python manage.py seed_demo

Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Next: python manage.py createsuperuser"
Write-Host "Then: python manage.py runserver"
