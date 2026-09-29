from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class SiteSettings(TimeStampedModel):
    site_name = models.CharField(max_length=160, default="Scientific Portfolio")
    owner_name = models.CharField(max_length=160, blank=True)
    professional_title = models.CharField(max_length=220, blank=True)
    tagline = models.CharField(max_length=260, blank=True)
    institution = models.CharField(max_length=220, blank=True)
    primary_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=300, blank=True)
    footer_text = models.CharField(max_length=300, blank=True)
    contact_notification_email = models.EmailField(blank=True)
    logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    favicon = models.ImageField(upload_to="branding/", blank=True, null=True)
    default_meta_title = models.CharField(max_length=180, blank=True)
    default_meta_description = models.CharField(max_length=320, blank=True)
    citation_source_label = models.CharField(max_length=100, default="Semantic Scholar")
    citation_sync_enabled = models.BooleanField(default=True)
    show_publication_metric = models.BooleanField(default=True)
    show_citation_metric = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Site settings"

    def __str__(self):
        return self.site_name

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Profile(TimeStampedModel):
    full_name = models.CharField(max_length=180)
    degrees = models.CharField(max_length=180, blank=True)
    current_title = models.CharField(max_length=240, blank=True, help_text="Current designation / professional title")
    department = models.CharField(max_length=220, blank=True)
    institution = models.CharField(max_length=220, blank=True)
    highest_education = models.CharField(max_length=260, blank=True, help_text="Highest academic qualification, e.g. PhD in Medical Physics")
    professional_specialty = models.CharField(max_length=220, blank=True, help_text="Primary professional specialty")
    academic_role = models.CharField(max_length=220, blank=True, help_text="Academic, teaching, or research role if applicable")
    professional_focus = models.CharField(max_length=500, blank=True, help_text="Short summary of major professional focus areas")
    homepage_summary_heading = models.CharField(max_length=180, default="Academic & Scientific Overview")
    short_bio = models.TextField(blank=True)
    full_bio = models.TextField(blank=True)
    research_statement = models.TextField(blank=True)
    research_interests = models.TextField(blank=True, help_text="Comma-separated research interests")
    clinical_interests = models.TextField(blank=True)
    keywords = models.CharField(max_length=500, blank=True, help_text="Comma-separated keywords")
    profile_photo = models.ImageField(upload_to="profile/", blank=True, null=True)
    location = models.CharField(max_length=180, blank=True)
    public_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name

    @property
    def research_interest_list(self):
        return [x.strip() for x in self.research_interests.split(",") if x.strip()]


class BannerSettings(TimeStampedModel):
    TRANSITIONS = [("slide", "Slide"), ("fade", "Fade")]
    DIRECTIONS = [("rtl", "Right to Left"), ("ltr", "Left to Right")]

    enabled = models.BooleanField(default=True)
    transition_type = models.CharField(max_length=20, choices=TRANSITIONS, default="fade")
    direction = models.CharField(max_length=10, choices=DIRECTIONS, default="rtl")
    autoplay = models.BooleanField(default=True)
    interval_ms = models.PositiveIntegerField(default=6500, validators=[MinValueValidator(2500), MaxValueValidator(30000)])
    transition_ms = models.PositiveIntegerField(default=900, validators=[MinValueValidator(150), MaxValueValidator(5000)])
    pause_on_hover = models.BooleanField(default=True)
    loop = models.BooleanField(default=True)
    show_arrows = models.BooleanField(default=True)
    show_dots = models.BooleanField(default=True)
    overlay_opacity = models.PositiveIntegerField(default=58, validators=[MinValueValidator(0), MaxValueValidator(90)], help_text="Dark overlay percentage over banner images")
    min_height_px = models.PositiveIntegerField(default=620, validators=[MinValueValidator(420), MaxValueValidator(900)])

    class Meta:
        verbose_name = "Homepage Banner"
        verbose_name_plural = "Homepage Banner"

    def __str__(self):
        return "Homepage banner settings"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class BannerSlide(TimeStampedModel):
    ALIGNMENTS = [("left", "Left"), ("center", "Center"), ("right", "Right")]

    banner = models.ForeignKey(
        BannerSettings,
        on_delete=models.CASCADE,
        related_name="slides",
        default=1,
        editable=False,
    )
    eyebrow = models.CharField(max_length=100, blank=True, default="Scientific Portfolio")
    title = models.CharField(max_length=220, blank=True, help_text="Leave blank to use the public profile name")
    subtitle = models.CharField(max_length=260, blank=True)
    description = models.TextField(blank=True)
    background_image = models.ImageField(upload_to="banners/backgrounds/", blank=True, null=True)
    foreground_image = models.ImageField(upload_to="banners/foreground/", blank=True, null=True, help_text="Optional portrait or subject image")

    primary_button_text = models.CharField(max_length=80, default="View Research", blank=True)
    primary_button_url = models.CharField(max_length=255, default="/research/", blank=True)
    secondary_button_text = models.CharField(max_length=80, default="View CV", blank=True)
    secondary_button_url = models.CharField(max_length=255, default="/cv/", blank=True)
    tertiary_button_text = models.CharField(max_length=80, default="Contact →", blank=True)
    tertiary_button_url = models.CharField(max_length=255, default="/contact/", blank=True)

    text_alignment = models.CharField(max_length=20, choices=ALIGNMENTS, default="left")
    display_order = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "Homepage Banner Slide"
        verbose_name_plural = "Homepage Banner Slides"

    def __str__(self):
        return self.title or self.subtitle or f"Banner slide {self.pk or ''}"


class HomePageSettings(TimeStampedModel):
    overview_title = models.CharField(max_length=180, default="Academic & Scientific Overview")
    show_overview = models.BooleanField(default=True)
    research_interests_title = models.CharField(max_length=180, default="Research Interests & Expertise")
    show_research_interests = models.BooleanField(default=True)
    show_metrics = models.BooleanField(default=True)
    recent_research_title = models.CharField(max_length=180, default="Recent Research")
    show_recent_research = models.BooleanField(default=True)
    recent_research_limit = models.PositiveIntegerField(default=6, validators=[MinValueValidator(3), MaxValueValidator(12)])
    show_featured_research = models.BooleanField(default=True)
    featured_research_title = models.CharField(max_length=180, default="Featured Research")
    featured_research_limit = models.PositiveIntegerField(default=6, validators=[MinValueValidator(1), MaxValueValidator(12)])
    professional_title = models.CharField(max_length=180, default="Academic & Professional Highlights")
    show_professional_highlights = models.BooleanField(default=True)
    professional_highlights_limit = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(8)])
    show_projects = models.BooleanField(default=True)
    projects_title = models.CharField(max_length=180, default="Selected Research Projects")
    show_hub = models.BooleanField(default=True)
    hub_title = models.CharField(max_length=180, default="Research Hub Highlights")
    show_people = models.BooleanField(default=True)
    people_title = models.CharField(max_length=180, default="Connected People")
    show_contact_cta = models.BooleanField(default=True)
    contact_eyebrow = models.CharField(max_length=100, default="Collaborate")
    contact_title = models.CharField(max_length=220, default="Research, academic, and professional inquiries")
    contact_text = models.TextField(default="Interested in scientific collaboration, invited lectures, research projects, or professional discussion? Send a structured inquiry through the contact page.")
    contact_button_text = models.CharField(max_length=80, default="Contact Me →")

    class Meta:
        verbose_name_plural = "Homepage settings"

    def __str__(self):
        return "Homepage settings"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AcademicProfile(TimeStampedModel):
    PLATFORM_CHOICES = [(x, x) for x in ["ORCID", "Google Scholar", "ResearchGate", "PubMed", "Scopus", "Web of Science", "LinkedIn", "GitHub", "Institutional Profile", "Other"]]
    platform = models.CharField(max_length=60, choices=PLATFORM_CHOICES)
    label = models.CharField(max_length=100, blank=True)
    url = models.URLField()
    display_order = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "platform"]

    def __str__(self):
        return self.label or self.platform


class SocialLink(TimeStampedModel):
    platform = models.CharField(max_length=80)
    label = models.CharField(max_length=100, blank=True)
    url = models.URLField()
    display_order = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)
    open_new_tab = models.BooleanField(default=True)
    class Meta:
        ordering = ["display_order", "platform"]
    def __str__(self):
        return self.label or self.platform


class CVSection(TimeStampedModel):
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)
    class Meta:
        ordering = ["display_order", "title"]
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title


class CVEntry(TimeStampedModel):
    section = models.ForeignKey(CVSection, on_delete=models.CASCADE, related_name="entries")
    title = models.CharField(max_length=220)
    subtitle = models.CharField(max_length=220, blank=True)
    institution = models.CharField(max_length=220, blank=True)
    location = models.CharField(max_length=180, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    url = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    visible = models.BooleanField(default=True)
    class Meta:
        ordering = ["section__display_order", "display_order", "-start_date"]
    def __str__(self):
        return self.title


class CVDocument(TimeStampedModel):
    title = models.CharField(max_length=180, default="Curriculum Vitae")
    file = models.FileField(upload_to="cv/")
    version = models.CharField(max_length=40, blank=True)
    effective_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=True)
    download_enabled = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.title} {self.version}".strip()


class Experience(TimeStampedModel):
    organization = models.CharField(max_length=220)
    position = models.CharField(max_length=220)
    department = models.CharField(max_length=220, blank=True)
    employment_type = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=180, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    currently_working = models.BooleanField(default=False)
    summary = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    organization_url = models.URLField(blank=True)
    logo = models.ImageField(upload_to="experience/", blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)
    class Meta:
        ordering = ["display_order", "-start_date"]
    def __str__(self):
        return f"{self.position} — {self.organization}"


class ResearchTheme(TimeStampedModel):
    name = models.CharField(max_length=140, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)
    class Meta:
        ordering = ["display_order", "name"]
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name


class Tag(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name


class ConnectedPerson(TimeStampedModel):
    RELATIONSHIP_CHOICES = [(x, x) for x in ["Collaborator", "Mentor", "Research Student", "Co-investigator", "Professional Colleague", "Other"]]
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    degrees = models.CharField(max_length=160, blank=True)
    title = models.CharField(max_length=220, blank=True)
    institution = models.CharField(max_length=220, blank=True)
    department = models.CharField(max_length=220, blank=True)
    country = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to="people/", blank=True, null=True)
    short_bio = models.TextField(blank=True)
    expertise = models.CharField(max_length=400, blank=True, help_text="Comma-separated")
    relationship_type = models.CharField(max_length=80, choices=RELATIONSHIP_CHOICES, default="Collaborator")
    orcid_url = models.URLField(blank=True)
    researchgate_url = models.URLField(blank=True)
    scholar_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)
    class Meta:
        ordering = ["display_order", "name"]
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name
    @property
    def expertise_list(self):
        return [x.strip() for x in self.expertise.split(",") if x.strip()]


class ResearchProject(TimeStampedModel):
    STATUS_CHOICES = [(x, x) for x in ["Planning", "Active", "Completed", "On Hold"]]
    title = models.CharField(max_length=240)
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default="Active")
    summary = models.TextField(blank=True)
    full_description = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    funding = models.CharField(max_length=240, blank=True)
    institution = models.CharField(max_length=220, blank=True)
    collaborators = models.ManyToManyField(ConnectedPerson, blank=True, related_name="projects")
    keywords = models.CharField(max_length=500, blank=True)
    theme = models.ForeignKey(ResearchTheme, on_delete=models.SET_NULL, blank=True, null=True, related_name="projects")
    project_url = models.URLField(blank=True)
    repository_url = models.URLField(blank=True)
    featured_image = models.ImageField(upload_to="projects/", blank=True, null=True)
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ["display_order", "-start_date", "title"]
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title


class Publication(TimeStampedModel):
    TYPE_CHOICES = [(x, x) for x in ["Journal Article", "Review", "Systematic Review", "Meta-analysis", "Book", "Book Chapter", "Conference Paper", "Conference Abstract", "Preprint", "Technical Report", "Dataset", "Software", "Project", "Other"]]
    STATUS_CHOICES = [(x, x) for x in ["Draft", "Accepted", "In Press", "Published", "Archived"]]
    title = models.CharField(max_length=400)
    slug = models.SlugField(max_length=420, unique=True, blank=True)
    publication_type = models.CharField(max_length=80, choices=TYPE_CHOICES, default="Journal Article")
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default="Published")
    authors = models.TextField(help_text="Author list in publication order")
    owner_author_position = models.PositiveIntegerField(blank=True, null=True)
    corresponding_author = models.BooleanField(default=False)
    journal = models.CharField(max_length=240, blank=True)
    publisher = models.CharField(max_length=220, blank=True)
    conference = models.CharField(max_length=240, blank=True)
    book_title = models.CharField(max_length=240, blank=True)
    year = models.PositiveIntegerField(blank=True, null=True, validators=[MinValueValidator(1900), MaxValueValidator(2200)])
    publication_date = models.DateField(blank=True, null=True)
    volume = models.CharField(max_length=50, blank=True)
    issue = models.CharField(max_length=50, blank=True)
    pages = models.CharField(max_length=80, blank=True)
    article_number = models.CharField(max_length=80, blank=True)
    doi = models.CharField(max_length=260, unique=True, blank=True, null=True)
    pmid = models.CharField(max_length=80, blank=True)
    arxiv_id = models.CharField(max_length=80, blank=True)
    abstract = models.TextField(blank=True)
    keywords = models.CharField(max_length=600, blank=True, help_text="Comma-separated")
    theme = models.ForeignKey(ResearchTheme, on_delete=models.SET_NULL, blank=True, null=True, related_name="publications")
    tags = models.ManyToManyField(Tag, blank=True, related_name="publications")
    collaborators = models.ManyToManyField(ConnectedPerson, blank=True, related_name="publications")
    external_url = models.URLField(blank=True)
    pdf = models.FileField(upload_to="publications/", blank=True, null=True)
    open_access = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to="publications/thumbnails/", blank=True, null=True)
    citation_count = models.PositiveIntegerField(default=0)
    citation_source = models.CharField(max_length=100, blank=True)
    citation_last_synced = models.DateTimeField(blank=True, null=True)
    metadata_last_synced = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    class Meta:
        ordering = ["-publication_date", "-year", "-created_at"]
    def save(self, *args, **kwargs):
        if self.doi:
            self.doi = self.doi.strip().replace("https://doi.org/", "").replace("http://doi.org/", "").replace("doi:", "").strip()
        if not self.slug:
            base = slugify(self.title)[:360] or "publication"
            slug = base
            n = 2
            while Publication.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        if self.publication_date and not self.year:
            self.year = self.publication_date.year
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse("research_detail", args=[self.slug])
    @property
    def doi_url(self):
        return f"https://doi.org/{self.doi}" if self.doi else ""
    @property
    def keyword_list(self):
        return [x.strip() for x in self.keywords.split(",") if x.strip()]


class CitationSnapshot(TimeStampedModel):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name="citation_snapshots")
    source = models.CharField(max_length=100)
    citation_count = models.PositiveIntegerField(default=0)
    retrieved_at = models.DateTimeField(auto_now_add=True)
    raw_identifier = models.CharField(max_length=260, blank=True)
    class Meta:
        ordering = ["-retrieved_at"]
    def __str__(self):
        return f"{self.publication_id}: {self.citation_count}"


class ResearchHubItem(TimeStampedModel):
    TYPE_CHOICES = [(x, x) for x in ["Project", "Dataset", "Software", "Protocol", "Method", "Educational Resource", "Presentation", "Poster", "Opportunity", "News", "Other"]]
    STATUS_CHOICES = [("Draft", "Draft"), ("Published", "Published"), ("Archived", "Archived")]
    title = models.CharField(max_length=260)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    content_type = models.CharField(max_length=80, choices=TYPE_CHOICES, default="Project")
    summary = models.TextField(blank=True)
    body = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="hub/", blank=True, null=True)
    file = models.FileField(upload_to="hub/files/", blank=True, null=True)
    external_url = models.URLField(blank=True)
    publication_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default="Published")
    featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True, related_name="hub_items")
    theme = models.ForeignKey(ResearchTheme, on_delete=models.SET_NULL, blank=True, null=True, related_name="hub_items")
    seo_title = models.CharField(max_length=180, blank=True)
    seo_description = models.CharField(max_length=320, blank=True)
    class Meta:
        ordering = ["display_order", "-publication_date", "-created_at"]
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse("hub_detail", args=[self.slug])


class ResearchHubBlock(TimeStampedModel):
    BLOCK_TYPES = [(x, x) for x in ["Heading", "Paragraph", "Image", "Download", "External Link", "Quote", "Code"]]
    hub_item = models.ForeignKey(ResearchHubItem, on_delete=models.CASCADE, related_name="blocks")
    block_type = models.CharField(max_length=40, choices=BLOCK_TYPES, default="Paragraph")
    heading = models.CharField(max_length=240, blank=True)
    body = models.TextField(blank=True)
    image = models.ImageField(upload_to="hub/blocks/", blank=True, null=True)
    file = models.FileField(upload_to="hub/blocks/files/", blank=True, null=True)
    url = models.URLField(blank=True)
    button_label = models.CharField(max_length=100, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)
    class Meta:
        ordering = ["display_order", "id"]
    def __str__(self):
        return self.heading or f"{self.block_type} block"


class EmailTemplate(TimeStampedModel):
    KEY_CHOICES = [("admin_notification", "Admin notification"), ("visitor_acknowledgement", "Visitor acknowledgement")]
    key = models.CharField(max_length=80, choices=KEY_CHOICES, unique=True)
    subject_template = models.CharField(max_length=240)
    body_template = models.TextField(help_text="Available fields: {reference}, {name}, {email}, {organization}, {country}, {inquiry_type}, {subject}, {message}, {owner_name}, {site_name}")
    enabled = models.BooleanField(default=True)
    def __str__(self):
        return self.get_key_display()


class ContactSubmission(TimeStampedModel):
    INQUIRY_CHOICES = [(x, x) for x in ["Research collaboration", "Academic invitation", "Conference / lecture", "Professional consultation", "Publication inquiry", "Student / research supervision", "Media inquiry", "General inquiry", "Other"]]
    STATUS_CHOICES = [(x, x) for x in ["New", "Read", "Replied", "Archived", "Spam"]]
    reference = models.CharField(max_length=40, unique=True, blank=True)
    name = models.CharField(max_length=160)
    email = models.EmailField()
    organization = models.CharField(max_length=220, blank=True)
    country = models.CharField(max_length=100, blank=True)
    inquiry_type = models.CharField(max_length=80, choices=INQUIRY_CHOICES)
    subject = models.CharField(max_length=220)
    message = models.TextField(max_length=5000)
    consent = models.BooleanField(default=False)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="New")
    admin_notes = models.TextField(blank=True)
    source_page = models.CharField(max_length=300, blank=True)
    ip_hash = models.CharField(max_length=128, blank=True)
    user_agent_summary = models.CharField(max_length=300, blank=True)
    replied_at = models.DateTimeField(blank=True, null=True)
    class Meta:
        ordering = ["-created_at"]
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.reference:
            self.reference = f"PORT-{self.created_at.year}-{self.pk:06d}"
            ContactSubmission.objects.filter(pk=self.pk).update(reference=self.reference)
    def __str__(self):
        return f"{self.reference or 'Inquiry'} — {self.name}"


class ContactResponse(TimeStampedModel):
    submission = models.ForeignKey(ContactSubmission, on_delete=models.CASCADE, related_name="responses")
    subject = models.CharField(max_length=220)
    body = models.TextField()
    sent_at = models.DateTimeField(blank=True, null=True)
    delivery_status = models.CharField(max_length=30, default="Pending")
    def __str__(self):
        return f"Reply to {self.submission.reference}"
