from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import ContactResponse, ContactSubmission

@receiver(post_save, sender=ContactResponse)
def send_contact_response(sender, instance, created, **kwargs):
    if not created or instance.sent_at:
        return
    status = "Sent"
    sent_at = timezone.now()
    try:
        EmailMultiAlternatives(instance.subject, instance.body, settings.DEFAULT_FROM_EMAIL, [instance.submission.email]).send(fail_silently=False)
        ContactSubmission.objects.filter(pk=instance.submission_id).update(status="Replied", replied_at=sent_at)
    except Exception:
        status = "Failed"
    ContactResponse.objects.filter(pk=instance.pk).update(delivery_status=status, sent_at=sent_at)
