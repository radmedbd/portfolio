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
    headers = {"User-Agent": "ScientificPortfolio/1.0"}
    if settings.SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = settings.SEMANTIC_SCHOLAR_API_KEY
    params = {"fields": "title,citationCount,externalIds,url"}
    r = requests.get(url, headers=headers, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def fetch_openalex_citations(doi: str) -> dict:
    doi = normalize_doi(doi)
    if not doi:
        raise ValueError("DOI is required")
    url = f"https://api.openalex.org/works/https://doi.org/{doi}"
    params = {}
    if getattr(settings, "OPENALEX_MAILTO", ""):
        params["mailto"] = settings.OPENALEX_MAILTO
    r = requests.get(url, params=params, headers={"User-Agent": "ScientificPortfolio/1.0"}, timeout=20)
    r.raise_for_status()
    return r.json()


def fetch_crossref_citation_count(doi: str) -> int:
    """Return Crossref's is-referenced-by-count for a DOI.

    This is used as a fallback when Semantic Scholar cannot resolve the DOI
    or its API is temporarily unavailable/rate-limited.
    """
    data = fetch_crossref_metadata(doi)
    return int(data.get("is-referenced-by-count") or 0)


def _store_citation_count(publication: Publication, count: int, source: str):
    publication.citation_count = max(0, int(count or 0))
    publication.citation_source = source
    publication.citation_last_synced = timezone.now()
    publication.save(update_fields=["citation_count", "citation_source", "citation_last_synced", "updated_at"])
    CitationSnapshot.objects.create(
        publication=publication,
        source=source,
        citation_count=publication.citation_count,
        raw_identifier=publication.doi or "",
    )
    return publication.citation_count


def sync_publication_citation(publication: Publication):
    """Sync one DOI using Semantic Scholar, then OpenAlex, then Crossref.

    The source actually used is stored on the publication and in CitationSnapshot.
    """
    doi = normalize_doi(publication.doi)
    if not doi:
        raise ValueError("Publication has no DOI")

    errors = []
    try:
        data = fetch_semantic_scholar_citations(doi)
        if data.get("paperId"):
            return _store_citation_count(publication, int(data.get("citationCount") or 0), "Semantic Scholar")
    except Exception as exc:
        errors.append(f"Semantic Scholar: {exc}")

    try:
        data = fetch_openalex_citations(doi)
        if data.get("id"):
            return _store_citation_count(publication, int(data.get("cited_by_count") or 0), "OpenAlex")
    except Exception as exc:
        errors.append(f"OpenAlex: {exc}")

    try:
        count = fetch_crossref_citation_count(doi)
        return _store_citation_count(publication, count, "Crossref")
    except Exception as exc:
        errors.append(f"Crossref: {exc}")

    raise RuntimeError("Citation lookup failed. " + " | ".join(errors))

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
    admin_to = settings_obj.contact_notification_email or settings_obj.primary_email or settings.CONTACT_NOTIFICATION_EMAIL
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
