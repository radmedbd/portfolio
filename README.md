# Scientific Portfolio CMS — Dynamic Banner Edition

A Django-based scientific portfolio with a fully dynamic public site and Django Admin CMS.

## What is included

- **No Home menu item** — the logo always links to `/` and acts as the Home control.
- Navigation: **Academic & Professional Profile, Research, Research Hub, Experience, Connected People, Contact**.
- **Dynamic homepage banner** with admin-controlled:
  - multiple slides;
  - background image;
  - optional foreground/profile image;
  - title, subtitle and description;
  - three CTA buttons;
  - slide/fade effect;
  - left-to-right/right-to-left direction;
  - autoplay, interval, transition speed, loop, pause on hover, arrows and dots;
  - overlay strength and banner height;
  - optional start/end publishing dates.
- Colorful **View Research**, **View CV**, and **Contact →** buttons with hover effects.
- Homepage academic/scientific summary including higher education, designation, institution, specialty, academic/research role and research interests.
- Automatic total publications, total citations and research-project metrics in the hero.
- Recent research automatically sorted newest first.
- Featured Research is populated automatically from publications marked **Featured**; there is no second slider control.
- Academic & Professional Profile page with dynamic profile fields, CV sections, academic profile links, print option and current CV PDF download.
- Publication database, DOI import/refresh, Semantic Scholar citation synchronization, projects, Research Hub, connected people, contact inbox, email automation, global search and SEO endpoints.

## Important: project folder

Run Django commands from the folder containing both `manage.py` and `requirements.txt`.

For the package layout used here, that is normally:

```powershell
E:\scientific_portfolio\scientific_portfolio
```

In PowerShell, enter it with:

```powershell
cd E:\scientific_portfolio\scientific_portfolio
```

Do **not** type `/e/scientific_portfolio/scientific_portfolio` in PowerShell. That notation is for Git Bash paths.

## PowerShell setup

If your virtual environment already exists at `E:\scientific_portfolio\.venv`, activate it first:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& E:\scientific_portfolio\.venv\Scripts\Activate.ps1
cd E:\scientific_portfolio\scientific_portfolio
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

**Create the application migration before opening the site:**

```powershell
python manage.py makemigrations core
python manage.py migrate
```

This step creates tables such as `core_profile`, `core_bannerslide`, and the other CMS tables.

Create the admin user:

```powershell
python manage.py createsuperuser
```

Load editable starter content if desired:

```powershell
python manage.py seed_demo
```

Run:

```powershell
python manage.py runserver
```

Public site:

```text
http://127.0.0.1:8000/
```

Admin:

```text
http://127.0.0.1:8000/admin/
```

### One-command setup helper

After activating the virtual environment and entering the project folder, you can alternatively run:

```powershell
.\setup_local.ps1
```

Then create your superuser and run the server.

## Git Bash setup

```bash
cd /e/scientific_portfolio/scientific_portfolio
source /e/scientific_portfolio/.venv/Scripts/activate
pip install -r requirements.txt
python manage.py makemigrations core
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

## Admin areas to edit first

After login, update these in this order:

1. **Site settings** — name, title, institution, logo, favicon, contact/SEO/metric settings.
2. **Profiles** — higher education, designation, institution, professional specialty, research role, biography and research interests.
3. **Homepage Banner** — one screen containing animation/direction/timing/appearance controls **and all banner slides inline**.
4. **Homepage settings** — show/hide and rename homepage sections, including Featured Research title/limit.
5. **CV sections / CV entries / CV documents** — the Academic & Professional Profile page.
6. **Publications** — add manually or use **Import by DOI**; tick **Featured** to place selected papers in the homepage Featured Research section.
7. Research projects, Research Hub, Connected People and academic/social profiles.

## Banner behavior

If no banner slide exists, the homepage automatically displays a fallback hero using the public Profile and Site Settings data. Once you add enabled slides inside **Admin → Homepage Banner**, those slides become the hero.

The default button targets are:

```text
View Research  → /research/
View CV        → /cv/
Contact →      → /contact/
```

Relative URLs are supported by the inline banner slides so internal links are easy to maintain.

## Publication and citation metrics

Homepage publication count is calculated from publications with status:

- Accepted
- In Press
- Published

Total citations are summed from those records. Citation source and last synchronization date are shown for scientific transparency.

Sync citation counts:

```powershell
python manage.py sync_citations
```

Refresh DOI metadata:

```powershell
python manage.py refresh_doi_metadata
```

Or use the actions directly from Django Admin → Publications.

## Contact workflow

A visitor submission is validated, rate-limited, stored in the database, assigned a `PORT-YEAR-XXXXXX` reference, shown in Admin, and can trigger admin/visitor email messages when email is configured.

Local development uses the console email backend by default, so messages print in the terminal.

## Production

- SQLite works locally.
- Set `DATABASE_URL` for PostgreSQL.
- Set `DEBUG=False`, a strong `SECRET_KEY`, `ALLOWED_HOSTS`, HTTPS/security settings, SMTP credentials, `DEFAULT_FROM_EMAIL`, `CROSSREF_MAILTO`, and optionally `SEMANTIC_SCHOLAR_API_KEY`.
- Run `python manage.py collectstatic` before production deployment.
- Back up database and uploaded media.

## SEO endpoints

- `/sitemap.xml`
- `/robots.txt`

The old `/about/` route redirects to `/cv/` because About content is now part of **Academic & Professional Profile**.


## Slider architecture (important)

This version intentionally has **one slider system only**: the dynamic homepage banner.

- **Homepage Banner** is the only slider-related Admin screen. It contains animation controls and all banner slides inline on the same page.
- Each inline banner slide controls its text, images, buttons, order and publication window.
- **Featured Research is not a second slider.** It is populated automatically from publications where `Featured = Yes`.

This avoids duplicate or confusing slider controls in Django Admin.
