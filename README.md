# Scientific Portfolio — Complete Django Build

A dynamic scientific/academic portfolio with Django Admin CMS, dynamic homepage banner, publication database, DOI import, citation synchronization, Academic & Professional Profile/CV, Research Hub, Connected People, experience timeline, contact inbox, Gmail automation, PostgreSQL/Render support, and conditional Cloudinary media storage.

## Navigation
The public navigation intentionally has no **Home** item. The logo links to `/`.

- Academic & Professional Profile
- Research
- Research Hub
- Experience
- Connected People
- Contact

## Local setup (PowerShell)
```powershell
cd F:\scientific_portfolio
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py makemigrations core
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

**Important:** commit the generated migration files before deploying to Render:
```powershell
git add core/migrations
git commit -m "Add initial database migrations"
git push
```

## Gmail automation
The project is preconfigured to use `physicist.cmch@gmail.com` as the sender/admin notification address. Do not put the normal Gmail password in `.env` or Render. Create a Google App Password after enabling 2-Step Verification, then set only:

```env
EMAIL_HOST_PASSWORD=your-16-character-app-password
```

Test locally:
```powershell
python manage.py test_email --to physicist.cmch@gmail.com
```

Without `EMAIL_HOST_PASSWORD`, local development uses Django's console email backend instead of failing.

## Cloudinary
Cloudinary is optional locally. If no Cloudinary credentials exist, uploads use local `media/`. In production, set `CLOUDINARY_URL` (simplest) or the three individual Cloudinary variables. Images use Cloudinary image storage; PDFs/documents use conditional raw storage.

## Citations
Citation synchronization uses DOI and tries, in order:
1. Semantic Scholar
2. OpenAlex
3. Crossref `is-referenced-by-count`

Run:
```powershell
python manage.py sync_citations
```
or use **Admin → Publications → Sync all citations**. The source and last sync time are stored per publication.

## Render
The repository includes `build.sh`. Configure Render:
- Build command: `bash build.sh`
- Start command: `gunicorn portfolio_project.wsgi:application`

Environment variables:
```text
PYTHON_VERSION=3.13.5
DEBUG=False
SECRET_KEY=<generated>
DATABASE_URL=<Render Postgres Internal Database URL>
ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://*.onrender.com
CLOUDINARY_URL=<Cloudinary URL>
EMAIL_HOST_USER=physicist.cmch@gmail.com
EMAIL_HOST_PASSWORD=<Gmail App Password>
DEFAULT_FROM_EMAIL=physicist.cmch@gmail.com
CONTACT_NOTIFICATION_EMAIL=physicist.cmch@gmail.com
CROSSREF_MAILTO=physicist.cmch@gmail.com
OPENALEX_MAILTO=physicist.cmch@gmail.com
SEMANTIC_SCHOLAR_API_KEY=<optional>
```

After deployment, create the production admin account from Render Shell:
```bash
python manage.py createsuperuser
```

## Contact workflow
A contact submission is saved first, assigned a reference number, then Gmail sends an admin notification and visitor acknowledgement. Admin replies created from Contact Responses are emailed to the visitor and the inquiry is marked Replied.

## Media warning
Local SQLite/media content is not automatically transferred to Render/PostgreSQL/Cloudinary. Production content should be entered through the production admin or migrated separately.
