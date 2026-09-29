from .models import AcademicProfile, ContactSubmission, ResearchProject, SiteSettings, SocialLink
from .services import portfolio_metrics

def global_context(request):
    ctx = {
        "site_settings": SiteSettings.get_solo(),
        "global_metrics": portfolio_metrics(),
        "academic_profiles": AcademicProfile.objects.filter(enabled=True),
        "social_links": SocialLink.objects.filter(enabled=True),
    }
    if request.path.startswith("/admin/"):
        ctx["portfolio_admin_metrics"] = {
            "new_inquiries": ContactSubmission.objects.filter(status="New").count(),
            "active_projects": ResearchProject.objects.filter(status="Active", published=True).count(),
        }
    return ctx
