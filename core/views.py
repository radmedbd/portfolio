from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import ContactForm
from .models import (
    BannerSettings,
    BannerSlide,
    CVDocument,
    CVSection,
    ConnectedPerson,
    Experience,
    HomePageSettings,
    Profile,
    Publication,
    ResearchHubItem,
    ResearchProject,
    ResearchTheme,
)
from .services import hash_ip, send_contact_emails


PUBLICATION_STATUSES = ["Accepted", "In Press", "Published"]


def home(request):
    profile = Profile.objects.filter(is_public=True).first()
    home_settings = HomePageSettings.get_solo()
    banner_settings = BannerSettings.get_solo()
    now = timezone.now()

    banner_slides = BannerSlide.objects.filter(banner=banner_settings, enabled=True).filter(
        Q(start_at__isnull=True) | Q(start_at__lte=now),
        Q(end_at__isnull=True) | Q(end_at__gte=now),
    )

    recent_publications = (
        Publication.objects.filter(status__in=PUBLICATION_STATUSES)
        .select_related("theme")
        .prefetch_related("tags")
        .order_by("-publication_date", "-year", "-created_at")[: home_settings.recent_research_limit]
    )
    featured_publications = (
        Publication.objects.filter(featured=True, status__in=PUBLICATION_STATUSES)
        .select_related("theme")
        .prefetch_related("tags")
        .order_by("-publication_date", "-year", "-created_at")[: home_settings.featured_research_limit]
    )
    projects = (
        ResearchProject.objects.filter(published=True)
        .select_related("theme")
        .order_by("-featured", "display_order", "-start_date")[:6]
    )
    themes = ResearchTheme.objects.filter(enabled=True)[:10]
    people = ConnectedPerson.objects.filter(enabled=True, featured=True)[:8]
    hub = (
        ResearchHubItem.objects.filter(status="Published")
        .select_related("theme")
        .prefetch_related("tags")
        .order_by("-featured", "display_order", "-publication_date")[:6]
    )
    experiences = Experience.objects.filter(published=True).order_by(
        "display_order", "-currently_working", "-start_date"
    )[: home_settings.professional_highlights_limit]

    return render(
        request,
        "home.html",
        {
            "profile": profile,
            "home_settings": home_settings,
            "banner_settings": banner_settings,
            "banner_slides": banner_slides,
            "recent_publications": recent_publications,
            "featured_publications": featured_publications,
            "projects": projects,
            "themes": themes,
            "people": people,
            "hub_items": hub,
            "experiences": experiences,
        },
    )


def about(request):
    """Legacy URL: About content now lives in Academic & Professional Profile."""
    return redirect("cv", permanent=False)


def cv(request):
    profile = Profile.objects.filter(is_public=True).first()
    sections = CVSection.objects.filter(enabled=True).prefetch_related("entries")
    doc = (
        CVDocument.objects.filter(is_current=True, download_enabled=True)
        .order_by("-effective_date", "-created_at")
        .first()
    )
    return render(
        request,
        "cv.html",
        {"profile": profile, "sections": sections, "cv_document": doc},
    )


def experience(request):
    return render(
        request,
        "experience.html",
        {"experiences": Experience.objects.filter(published=True)},
    )


def research_list(request):
    qs = (
        Publication.objects.filter(status__in=PUBLICATION_STATUSES)
        .select_related("theme")
        .prefetch_related("tags")
        .order_by("-publication_date", "-year", "-created_at")
    )
    q = request.GET.get("q", "").strip()
    year = request.GET.get("year", "").strip()
    ptype = request.GET.get("type", "").strip()
    theme = request.GET.get("theme", "").strip()
    tag = request.GET.get("tag", "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(authors__icontains=q)
            | Q(journal__icontains=q)
            | Q(keywords__icontains=q)
            | Q(abstract__icontains=q)
        )
    if year:
        qs = qs.filter(year=year)
    if ptype:
        qs = qs.filter(publication_type=ptype)
    if theme:
        qs = qs.filter(theme__slug=theme)
    if tag:
        qs = qs.filter(tags__slug=tag)
    years = (
        Publication.objects.exclude(year=None)
        .values_list("year", flat=True)
        .distinct()
        .order_by("-year")
    )
    paginator = Paginator(qs.distinct(), 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "research_list.html",
        {
            "publications": page_obj.object_list,
            "page_obj": page_obj,
            "years": years,
            "type_choices": Publication.TYPE_CHOICES,
            "themes": ResearchTheme.objects.filter(enabled=True),
            "filters": request.GET,
        },
    )


def research_detail(request, slug):
    pub = get_object_or_404(
        Publication.objects.select_related("theme").prefetch_related("tags", "collaborators"),
        slug=slug,
        status__in=PUBLICATION_STATUSES,
    )
    related = (
        Publication.objects.filter(theme=pub.theme, status__in=PUBLICATION_STATUSES)
        .exclude(pk=pub.pk)[:4]
        if pub.theme
        else Publication.objects.none()
    )
    return render(request, "research_detail.html", {"publication": pub, "related": related})


def projects(request):
    return render(
        request,
        "projects.html",
        {
            "projects": ResearchProject.objects.filter(published=True)
            .select_related("theme")
            .prefetch_related("collaborators")
        },
    )


def hub_list(request):
    qs = ResearchHubItem.objects.filter(status="Published").select_related("theme").prefetch_related("tags")
    kind = request.GET.get("type", "")
    if kind:
        qs = qs.filter(content_type=kind)
    return render(
        request,
        "hub_list.html",
        {"items": qs, "type_choices": ResearchHubItem.TYPE_CHOICES, "current_type": kind},
    )


def hub_detail(request, slug):
    item = get_object_or_404(
        ResearchHubItem.objects.select_related("theme").prefetch_related("tags"),
        slug=slug,
        status="Published",
    )
    return render(request, "hub_detail.html", {"item": item})


def people_list(request):
    return render(request, "people_list.html", {"people": ConnectedPerson.objects.filter(enabled=True)})


def people_detail(request, slug):
    person = get_object_or_404(ConnectedPerson, slug=slug, enabled=True)
    return render(request, "people_detail.html", {"person": person})


def contact(request):
    if request.method == "POST":
        ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")
        key = f"contact-rate:{hash_ip(ip)}"
        count = cache.get(key, 0)
        if count >= 5:
            messages.error(request, "Too many submissions. Please try again later.")
            return render(request, "contact.html", {"form": ContactForm(request.POST)}, status=429)
        form = ContactForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.ip_hash = hash_ip(ip)
            submission.user_agent_summary = request.META.get("HTTP_USER_AGENT", "")[:300]
            submission.source_page = request.META.get("HTTP_REFERER", "")[:300]
            submission.save()
            cache.set(key, count + 1, 15 * 60)
            try:
                send_contact_emails(submission)
            except Exception:
                pass
            return HttpResponseRedirect(reverse("contact_success") + f"?ref={submission.reference}")
    else:
        form = ContactForm()
    return render(request, "contact.html", {"form": form})


def contact_success(request):
    return render(request, "contact_success.html", {"reference": request.GET.get("ref", "")})


def search(request):
    q = request.GET.get("q", "").strip()
    pubs = projects_qs = hub = people = []
    if q:
        pubs = Publication.objects.filter(status__in=PUBLICATION_STATUSES).filter(
            Q(title__icontains=q)
            | Q(authors__icontains=q)
            | Q(abstract__icontains=q)
            | Q(keywords__icontains=q)
        )[:20]
        projects_qs = ResearchProject.objects.filter(published=True).filter(
            Q(title__icontains=q) | Q(summary__icontains=q) | Q(keywords__icontains=q)
        )[:20]
        hub = ResearchHubItem.objects.filter(status="Published").filter(
            Q(title__icontains=q) | Q(summary__icontains=q) | Q(body__icontains=q)
        )[:20]
        people = ConnectedPerson.objects.filter(enabled=True).filter(
            Q(name__icontains=q) | Q(institution__icontains=q) | Q(expertise__icontains=q)
        )[:20]
    return render(
        request,
        "search_results.html",
        {
            "q": q,
            "publications": pubs,
            "projects": projects_qs,
            "hub_items": hub,
            "people": people,
        },
    )


def sitemap_xml(request):
    static_names = ["home", "cv", "experience", "research_list", "projects", "hub_list", "people_list", "contact"]
    urls = [request.build_absolute_uri(reverse(name)) for name in static_names]
    urls += [
        request.build_absolute_uri(pub.get_absolute_url())
        for pub in Publication.objects.filter(status__in=PUBLICATION_STATUSES)
    ]
    urls += [
        request.build_absolute_uri(item.get_absolute_url())
        for item in ResearchHubItem.objects.filter(status="Published")
    ]
    urls += [
        request.build_absolute_uri(reverse("people_detail", args=[p.slug]))
        for p in ConnectedPerson.objects.filter(enabled=True)
    ]
    body = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    body += "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    body += "\n</urlset>"
    return HttpResponse(body, content_type="application/xml")


def robots_txt(request):
    sitemap = request.build_absolute_uri(reverse("sitemap_xml"))
    return HttpResponse(
        f"User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {sitemap}\n",
        content_type="text/plain",
    )
