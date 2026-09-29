from django.contrib import admin, messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from .models import *
from .services import fetch_crossref_metadata, apply_crossref_metadata, normalize_doi, sync_publication_citation
from .forms import DOIImportForm

admin.site.site_header = "Scientific Portfolio Administration"
admin.site.site_title = "Portfolio Admin"
admin.site.index_title = "Content Management"
admin.site.index_template = "admin/custom_index.html"

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (("Identity", {"fields": ("site_name", "owner_name", "professional_title", "tagline", "institution")}), ("Contact", {"fields": ("primary_email", "phone", "address", "contact_notification_email")}), ("Branding", {"fields": ("logo", "favicon", "footer_text")}), ("Metrics & SEO", {"fields": ("citation_source_label", "citation_sync_enabled", "show_publication_metric", "show_citation_metric", "default_meta_title", "default_meta_description")}))
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "current_title", "highest_education", "institution", "is_public")
    fieldsets = (
        ("Identity", {"fields": ("full_name", "degrees", "profile_photo", "is_public")}),
        ("Current academic & professional profile", {"fields": ("current_title", "department", "institution", "highest_education", "professional_specialty", "academic_role", "professional_focus")}),
        ("Homepage summary", {"fields": ("homepage_summary_heading", "short_bio", "research_interests", "clinical_interests", "keywords")}),
        ("Extended profile", {"fields": ("full_bio", "research_statement")}),
        ("Public contact", {"fields": ("location", "public_email", "phone")}),
    )


class BannerSlideInline(admin.StackedInline):
    model = BannerSlide
    extra = 0
    fields = (
        ("enabled", "display_order"),
        "eyebrow",
        "title",
        "subtitle",
        "description",
        "text_alignment",
        ("background_image", "foreground_image"),
        ("primary_button_text", "primary_button_url"),
        ("secondary_button_text", "secondary_button_url"),
        ("tertiary_button_text", "tertiary_button_url"),
        ("start_at", "end_at"),
    )
    show_change_link = False


@admin.register(BannerSettings)
class BannerSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Banner status", {"fields": ("enabled",)}),
        ("Animation", {"fields": ("transition_type", "direction", "autoplay", "interval_ms", "transition_ms", "pause_on_hover", "loop", "show_arrows", "show_dots")}),
        ("Appearance", {"fields": ("overlay_opacity", "min_height_px")}),
    )
    inlines = [BannerSlideInline]

    def has_add_permission(self, request):
        return not BannerSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HomePageSettings)
class HomePageSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Academic & scientific overview", {"fields": ("show_overview", "overview_title", "show_research_interests", "research_interests_title", "show_metrics")}),
        ("Research", {"fields": ("show_recent_research", "recent_research_title", "recent_research_limit", "show_featured_research", "featured_research_title", "featured_research_limit", "show_projects", "projects_title")}),
        ("Professional highlights", {"fields": ("show_professional_highlights", "professional_title", "professional_highlights_limit")}),
        ("Research Hub & network", {"fields": ("show_hub", "hub_title", "show_people", "people_title")}),
        ("Contact CTA", {"fields": ("show_contact_cta", "contact_eyebrow", "contact_title", "contact_text", "contact_button_text")}),
    )
    def has_add_permission(self, request):
        return not HomePageSettings.objects.exists()

@admin.register(AcademicProfile)
class AcademicProfileAdmin(admin.ModelAdmin):
    list_display = ("platform", "label", "enabled", "display_order")
    list_editable = ("enabled", "display_order")

@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("platform", "label", "enabled", "display_order")
    list_editable = ("enabled", "display_order")

class CVEntryInline(admin.TabularInline):
    model = CVEntry
    extra = 0

@admin.register(CVSection)
class CVSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "display_order", "enabled")
    list_editable = ("display_order", "enabled")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CVEntryInline]

@admin.register(CVEntry)
class CVEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "institution", "start_date", "end_date", "visible", "display_order")
    list_filter = ("section", "visible", "is_current")
    search_fields = ("title", "institution", "description", "achievements")

admin.site.register(CVDocument)

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("position", "organization", "start_date", "end_date", "currently_working", "published", "display_order")
    list_editable = ("published", "display_order")
    search_fields = ("position", "organization", "summary")

@admin.register(ResearchTheme)
class ResearchThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order", "enabled")
    list_editable = ("display_order", "enabled")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

@admin.action(description="Refresh metadata from Crossref")
def refresh_crossref(modeladmin, request, queryset):
    ok = fail = 0
    for pub in queryset.exclude(doi__isnull=True).exclude(doi=""):
        try:
            apply_crossref_metadata(pub, fetch_crossref_metadata(pub.doi), overwrite=False)
            ok += 1
        except Exception as exc:
            fail += 1
            messages.warning(request, f"{pub.title[:60]}: {exc}")
    messages.success(request, f"Crossref refreshed: {ok}; failed: {fail}")

@admin.action(description="Sync citation counts from Semantic Scholar")
def sync_citations(modeladmin, request, queryset):
    ok = fail = 0
    for pub in queryset.exclude(doi__isnull=True).exclude(doi=""):
        try:
            sync_publication_citation(pub)
            ok += 1
        except Exception as exc:
            fail += 1
            messages.warning(request, f"{pub.title[:60]}: {exc}")
    messages.success(request, f"Citation sync: {ok}; failed: {fail}")

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    change_list_template = "admin/publication_changelist.html"
    list_display = ("title", "publication_type", "year", "status", "featured", "citation_count", "citation_last_synced")
    list_filter = ("status", "publication_type", "year", "featured", "open_access", "theme")
    search_fields = ("title", "authors", "journal", "doi", "keywords")
    filter_horizontal = ("tags", "collaborators")
    readonly_fields = ("citation_count", "citation_source", "citation_last_synced", "metadata_last_synced")
    actions = [refresh_crossref, sync_citations]
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Core", {"fields": ("title", "slug", "publication_type", "status", "authors", "owner_author_position", "corresponding_author")}),
        ("Bibliographic metadata", {"fields": ("journal", "publisher", "conference", "book_title", "year", "publication_date", "volume", "issue", "pages", "article_number", "doi", "pmid", "arxiv_id")}),
        ("Scientific content", {"fields": ("abstract", "keywords", "theme", "tags", "collaborators")}),
        ("Access & presentation", {"fields": ("external_url", "pdf", "open_access", "featured", "thumbnail")}),
        ("Citation metadata", {"fields": ("citation_count", "citation_source", "citation_last_synced", "metadata_last_synced")}),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom = [path("import-doi/", self.admin_site.admin_view(self.import_doi_view), name="core_publication_import_doi")]
        return custom + urls

    def import_doi_view(self, request):
        form = DOIImportForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            doi = normalize_doi(form.cleaned_data["doi"])
            existing = Publication.objects.filter(doi=doi).first()
            if existing:
                self.message_user(request, "That DOI already exists; opening the existing record.", level=messages.WARNING)
                return redirect(reverse("admin:core_publication_change", args=[existing.pk]))
            try:
                data = fetch_crossref_metadata(doi)
                title = (data.get("title") or [doi])[0]
                authors = []
                for author in data.get("author", []):
                    name = " ".join(x for x in [author.get("given", ""), author.get("family", "")] if x).strip()
                    if name:
                        authors.append(name)
                pub = Publication.objects.create(title=title or doi, authors=", ".join(authors), doi=doi, status="Published")
                apply_crossref_metadata(pub, data, overwrite=True)
                self.message_user(request, "Publication imported from Crossref. Review the record, add tags/themes, then save.", level=messages.SUCCESS)
                return redirect(reverse("admin:core_publication_change", args=[pub.pk]))
            except Exception as exc:
                self.message_user(request, f"DOI import failed: {exc}", level=messages.ERROR)
        context = {**self.admin_site.each_context(request), "title": "Import publication by DOI", "form": form, "opts": self.model._meta}
        return TemplateResponse(request, "admin/publication_import_doi.html", context)

@admin.register(CitationSnapshot)
class CitationSnapshotAdmin(admin.ModelAdmin):
    list_display = ("publication", "source", "citation_count", "retrieved_at")
    readonly_fields = ("publication", "source", "citation_count", "retrieved_at", "raw_identifier")
    def has_add_permission(self, request): return False

@admin.register(ConnectedPerson)
class ConnectedPersonAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "institution", "relationship_type", "featured", "enabled", "display_order")
    list_filter = ("relationship_type", "country", "featured", "enabled")
    list_editable = ("featured", "enabled", "display_order")
    search_fields = ("name", "institution", "expertise")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "theme", "featured", "published", "display_order")
    list_filter = ("status", "theme", "featured", "published")
    list_editable = ("featured", "published", "display_order")
    filter_horizontal = ("collaborators",)
    prepopulated_fields = {"slug": ("title",)}

class ResearchHubBlockInline(admin.StackedInline):
    model = ResearchHubBlock
    extra = 0

@admin.register(ResearchHubItem)
class ResearchHubItemAdmin(admin.ModelAdmin):
    list_display = ("title", "content_type", "status", "publication_date", "featured", "display_order")
    list_filter = ("content_type", "status", "featured", "theme")
    list_editable = ("featured", "display_order")
    filter_horizontal = ("tags",)
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ResearchHubBlockInline]

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("key", "subject_template", "enabled", "updated_at")
    list_editable = ("enabled",)

class ContactResponseInline(admin.StackedInline):
    model = ContactResponse
    extra = 0
    readonly_fields = ("sent_at", "delivery_status")

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("reference", "name", "email", "organization", "inquiry_type", "status", "created_at")
    list_filter = ("status", "inquiry_type", "country", "created_at")
    search_fields = ("reference", "name", "email", "organization", "subject", "message", "admin_notes")
    readonly_fields = ("reference", "name", "email", "organization", "country", "inquiry_type", "subject", "message", "consent", "source_page", "ip_hash", "user_agent_summary", "created_at", "updated_at")
    inlines = [ContactResponseInline]

@admin.register(ContactResponse)
class ContactResponseAdmin(admin.ModelAdmin):
    list_display = ("submission", "subject", "delivery_status", "sent_at")
    readonly_fields = ("sent_at", "delivery_status")
