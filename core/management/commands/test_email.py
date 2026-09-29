from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Send a test email using the configured Gmail/SMTP backend."
    def add_arguments(self, parser):
        parser.add_argument("--to", default=settings.CONTACT_NOTIFICATION_EMAIL)
    def handle(self, *args, **options):
        recipient = options["to"]
        sent = send_mail(
            "Scientific Portfolio email test",
            "Your Django portfolio Gmail automation is configured correctly.",
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        self.stdout.write(self.style.SUCCESS(f"Sent={sent} to {recipient}"))
