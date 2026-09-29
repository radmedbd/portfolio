import hashlib
import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum
from django.utils import timezone
from .models import CitationSnapshot, EmailTemplate, Publication, ResearchProject, SiteSettings


def hash_ip(ip: str) -> str:
    if not ip:
        return ""
    salt = settings.SECRET_KEY[:24]
    return hashlib.sha256(f"{salt}:{ip}".encode()).hexdigest()


def normalize_doi(value: str) -> str:
    if not value:
        return ""
    value = value.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if value.lower().startswith(prefix):
            value = value[len(prefix):]
    return value.strip()


def fetch_crossref_metadata(doi: str) -> dict:
    doi = normalize_doi(doi)
    if not doi:
        raise ValueError("DOI is required")
    url = f"https://api.crossref.org/works/doi/{doi}"
    headers = {"User-Agent": f"ScientificPortfolio/1.0 (mailto:{settings.CROSSREF_MAILTO})"}
    r = requests.get(url, headers=headers, params={"mailto": settings.CROSSREF_MAILTO}, timeout=20)
    r.raise_for_status()
    return r.json()["message"]


def apply_crossref_metadata(publication: Publication, data: dict, overwrite=False):
    def setv(field, value):
        if value in (None, "", []):
            return
        if overwrite or not getattr(publication, field):
            setattr(publication, field, value)

    title = (data.get("title") or [""])[0]
    container = (data.get("container-title") or [""])[0]
    authors = []
    for a in data.get("author", []):
        name = " ".join(x for x in [a.get("given", ""), a.get("family", "")] if x).strip()
        if name:
            authors.append(name)
    setv("title", title)
    setv("journal", container)
    setv("publisher", data.get("publisher", ""))
    setv("volume", data.get("volume", ""))
    setv("issue", data.get("issue", ""))
    setv("pages", data.get("page", ""))
    setv("authors", ", ".join(authors))
    setv("external_url", data.get("URL", ""))
    published = data.get("published-print") or data.get("published-online") or data.get("published") or {}
    date_parts = published.get("date-parts", [])
    if date_parts and date_parts[0]:
        parts = date_parts[0]
        year = parts[0]
        month = parts[1] if len(parts) > 1 else 1
        day = parts[2] if len(parts) > 2 else 1
        try:
            from datetime import date
            setv("publication_date", date(year, month, day))
            setv("year", year)
        except ValueError:
            setv("year", year)
    publication.metadata_last_synced = timezone.now()
    publication.save()
    return publication


def fetch_semantic_scholar_citations(doi: str) -> dict:
    doi = normalize_doi(doi)
    if not doi:
        raise ValueError("DOI is required")
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"
    headers = {}
    if settings.SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = settings.SEMANTIC_SCHOLAR_API_KEY
    params = {"fields": "title,citationCount,externalIds,url"}
    r = requests.get(url, headers=headers, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def sync_publication_citation(publication: Publication):
    data = fetch_semantic_scholar_citations(publication.doi)
    count = int(data.get("citationCount") or 0)
    publication.citation_count = count
    publication.citation_source = "Semantic Scholar"
    publication.citation_last_synced = timezone.now()
    publication.save(update_fields=["citation_count", "citation_source", "citation_last_synced", "updated_at"])
    CitationSnapshot.objects.create(publication=publication, source="Semantic Scholar", citation_count=count, raw_identifier=publication.doi or "")
    return count


def portfolio_metrics():
    qs = Publication.objects.filter(status__in=["Accepted", "In Press", "Published"])
    return {
        "total_publications": qs.count(),
        "total_citations": qs.aggregate(v=Sum("citation_count"))["v"] or 0,
        "total_projects": ResearchProject.objects.filter(published=True).count(),
        "active_projects": ResearchProject.objects.filter(published=True, status="Active").count(),
        "last_citation_sync": qs.exclude(citation_last_synced=None).order_by("-citation_last_synced").values_list("citation_last_synced", flat=True).first(),
    }


def _format_email_template(key, submission, default_subject, default_body, settings_obj):
    context = {
        "reference": submission.reference, "name": submission.name, "email": submission.email,
        "organization": submission.organization or "-", "country": submission.country or "-",
        "inquiry_type": submission.inquiry_type, "subject": submission.subject, "message": submission.message,
        "owner_name": settings_obj.owner_name or settings_obj.site_name, "site_name": settings_obj.site_name,
    }
    template = EmailTemplate.objects.filter(key=key, enabled=True).first()
    subject = template.subject_template if template else default_subject
    body = template.body_template if template else default_body
    try:
        return subject.format_map(context), body.format_map(context)
    except (KeyError, ValueError):
        return default_subject.format_map(context), default_body.format_map(context)


def send_contact_emails(submission):
    settings_obj = SiteSettings.get_solo()
    admin_to = settings_obj.contact_notification_email or settings_obj.primary_email
    admin_subject_default = "New portfolio inquiry: {inquiry_type}"
    admin_body_default = (
        "A new inquiry has been submitted through your scientific portfolio.\n\n"
        "Reference: {reference}\nName: {name}\nEmail: {email}\n"
        "Institution: {organization}\nCountry: {country}\nInquiry type: {inquiry_type}\n"
        "Subject: {subject}\n\nMessage:\n{message}\n"
    )
    if admin_to:
        subject, body = _format_email_template("admin_notification", submission, admin_subject_default, admin_body_default, settings_obj)
        EmailMultiAlternatives(subject, body, settings.DEFAULT_FROM_EMAIL, [admin_to]).send(fail_silently=False)

    visitor_subject_default = "Your message has been received"
    visitor_body_default = (
        "Dear {name},\n\nThank you for contacting me through my scientific portfolio. "
        "Your inquiry has been received successfully.\n\nReference: {reference}\nSubject: {subject}\n\n"
        "I will review your message and respond where appropriate.\n\nBest regards\n{owner_name}"
    )
    visitor_subject, visitor_body = _format_email_template("visitor_acknowledgement", submission, visitor_subject_default, visitor_body_default, settings_obj)
    EmailMultiAlternatives(visitor_subject, visitor_body, settings.DEFAULT_FROM_EMAIL, [submission.email]).send(fail_silently=True)
