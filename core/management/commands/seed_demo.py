from datetime import date

from django.core.management.base import BaseCommand

from core.models import (
    AcademicProfile,
    BannerSettings,
    BannerSlide,
    ConnectedPerson,
    CVEntry,
    CVSection,
    EmailTemplate,
    HomePageSettings,
    Profile,
    Publication,
    ResearchHubItem,
    ResearchProject,
    ResearchTheme,
    SiteSettings,
)


class Command(BaseCommand):
    help = "Create editable demonstration content for the scientific portfolio."

    def handle(self, *args, **options):
        settings = SiteSettings.get_solo()
        settings.site_name = "Scientific Portfolio"
        settings.owner_name = "Md. Akhtaruzzaman"
        settings.professional_title = "Medical Physicist • Researcher • Educator"
        settings.tagline = "Clinical medical physics • Research • Education • Innovation"
        settings.institution = "Evercare Hospital Chattogram"
        settings.footer_text = "Scientific portfolio, research profile, academic activities, and professional work."
        settings.save()

        profile, created = Profile.objects.get_or_create(
            full_name="Md. Akhtaruzzaman",
            defaults={
                "degrees": "PhD",
                "current_title": "Chief Medical Physicist",
                "department": "Radiation Oncology",
                "institution": "Evercare Hospital Chattogram",
                "highest_education": "PhD",
                "professional_specialty": "Radiotherapy Medical Physics",
                "academic_role": "Researcher and Medical Physics Educator",
                "professional_focus": "Radiotherapy quality assurance, treatment planning, dosimetry, medical imaging, automation, and artificial intelligence.",
                "homepage_summary_heading": "Academic & Scientific Overview",
                "short_bio": "Medical physicist, researcher, and educator with clinical and research interests spanning advanced radiotherapy, patient-specific quality assurance, dosimetry, medical imaging, and artificial intelligence.",
                "full_bio": "This profile is fully editable from Django Admin. Replace or expand this text with your preferred professional biography.",
                "research_statement": "My research interests focus on clinically useful methods that improve radiotherapy quality, safety, efficiency, and accessibility.",
                "research_interests": "Artificial Intelligence in Radiotherapy, Patient-Specific Quality Assurance, Advanced Treatment Planning, Radiotherapy Dosimetry, Medical Imaging, Independent Dose Verification, Radiation Protection, Clinical Medical Physics",
                "is_public": True,
            },
        )
        if not created:
            # Do not overwrite an already customized profile.
            self.stdout.write("Existing profile preserved.")

        banner_settings = BannerSettings.get_solo()
        HomePageSettings.get_solo()

        BannerSlide.objects.get_or_create(
            banner=banner_settings,
            title="Md. Akhtaruzzaman, PhD",
            defaults={
                "eyebrow": "Scientific Portfolio",
                "subtitle": "Medical Physicist • Researcher • Educator",
                "description": "Clinical medical physics, advanced radiotherapy, quality assurance, dosimetry, medical imaging, artificial intelligence, and scientific education.",
                "primary_button_text": "View Research",
                "primary_button_url": "/research/",
                "secondary_button_text": "View CV",
                "secondary_button_url": "/cv/",
                "tertiary_button_text": "Contact →",
                "tertiary_button_url": "/contact/",
                "display_order": 1,
                "enabled": True,
            },
        )
        BannerSlide.objects.get_or_create(
            banner=banner_settings,
            title="Research in Medical Physics",
            defaults={
                "eyebrow": "Research & Innovation",
                "subtitle": "From clinical quality assurance to AI-driven decision support",
                "description": "Explore recent publications, active research, scientific resources, and collaborative work.",
                "primary_button_text": "View Research",
                "primary_button_url": "/research/",
                "secondary_button_text": "View CV",
                "secondary_button_url": "/cv/",
                "tertiary_button_text": "Contact →",
                "tertiary_button_url": "/contact/",
                "display_order": 2,
                "enabled": True,
            },
        )

        AcademicProfile.objects.get_or_create(
            platform="ORCID",
            url="https://orcid.org/",
            defaults={"label": "ORCID", "display_order": 1, "enabled": False},
        )

        theme, _ = ResearchTheme.objects.get_or_create(
            name="Artificial Intelligence in Radiotherapy",
            defaults={
                "description": "Machine learning, automation, decision support, and intelligent quality assurance in radiotherapy.",
                "display_order": 1,
            },
        )

        Publication.objects.get_or_create(
            title="Example machine-learning study in radiotherapy quality assurance",
            defaults={
                "publication_type": "Journal Article",
                "status": "Published",
                "authors": "Md. Akhtaruzzaman, Collaborator One",
                "journal": "Example Journal",
                "year": 2026,
                "publication_date": date(2026, 9, 1),
                "abstract": "Replace this demonstration record with your publication metadata or import a publication by DOI from the admin panel.",
                "keywords": "patient-specific QA, machine learning, VMAT",
                "theme": theme,
                "featured": True,
                "citation_count": 0,
            },
        )

        ResearchProject.objects.get_or_create(
            title="Example Research Project",
            defaults={
                "status": "Active",
                "summary": "Replace this record with an active research project.",
                "theme": theme,
                "featured": True,
            },
        )

        ConnectedPerson.objects.get_or_create(
            name="Dr. Example Collaborator",
            defaults={
                "title": "Professor",
                "institution": "Example University",
                "relationship_type": "Collaborator",
                "expertise": "Medical Physics, Artificial Intelligence",
                "featured": True,
            },
        )

        ResearchHubItem.objects.get_or_create(
            title="Research Hub Example",
            defaults={
                "content_type": "Educational Resource",
                "summary": "A structured scientific resource can be published here.",
                "status": "Published",
                "theme": theme,
                "featured": True,
            },
        )

        education, _ = CVSection.objects.get_or_create(
            title="Higher Education",
            defaults={"display_order": 1, "enabled": True},
        )
        CVEntry.objects.get_or_create(
            section=education,
            title="Doctoral Degree",
            defaults={
                "subtitle": "Replace with degree title, university, and details",
                "description": "This demonstration CV entry is editable from Admin → CV Sections / CV Entries.",
                "display_order": 1,
            },
        )

        appointment, _ = CVSection.objects.get_or_create(
            title="Current Appointment",
            defaults={"display_order": 2, "enabled": True},
        )
        CVEntry.objects.get_or_create(
            section=appointment,
            title="Chief Medical Physicist",
            defaults={
                "institution": "Evercare Hospital Chattogram",
                "subtitle": "Radiation Oncology",
                "is_current": True,
                "display_order": 1,
            },
        )

        EmailTemplate.objects.get_or_create(
            key="admin_notification",
            defaults={
                "subject_template": "New portfolio inquiry: {inquiry_type}",
                "body_template": "Reference: {reference}\nName: {name}\nEmail: {email}\nInstitution: {organization}\nSubject: {subject}\n\n{message}",
            },
        )
        EmailTemplate.objects.get_or_create(
            key="visitor_acknowledgement",
            defaults={
                "subject_template": "Your message has been received",
                "body_template": "Dear {name},\n\nThank you for contacting me. Your reference is {reference}.\n\nBest regards\n{owner_name}",
            },
        )

        self.stdout.write(self.style.SUCCESS("Portfolio demonstration content created."))
        self.stdout.write("Upload your logo/profile/banner images and edit all text from Django Admin.")
