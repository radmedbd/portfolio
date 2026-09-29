from django.core.management.base import BaseCommand
from core.models import Publication
from core.services import sync_publication_citation

class Command(BaseCommand):
    help = "Sync citation counts for publications that have a DOI."
    def handle(self, *args, **options):
        ok = fail = 0
        for pub in Publication.objects.exclude(doi__isnull=True).exclude(doi=""):
            try:
                count = sync_publication_citation(pub)
                self.stdout.write(self.style.SUCCESS(f"{pub.id}: {count} — {pub.title[:70]}"))
                ok += 1
            except Exception as exc:
                self.stderr.write(f"{pub.id}: {exc}")
                fail += 1
        self.stdout.write(f"Done. Success={ok}, failed={fail}")
