from django.core.management.base import BaseCommand
from core.models import Publication
from core.services import fetch_crossref_metadata, apply_crossref_metadata

class Command(BaseCommand):
    help = "Refresh missing publication metadata from Crossref using DOI."
    def handle(self, *args, **options):
        ok = fail = 0
        for pub in Publication.objects.exclude(doi__isnull=True).exclude(doi=""):
            try:
                apply_crossref_metadata(pub, fetch_crossref_metadata(pub.doi), overwrite=False)
                self.stdout.write(self.style.SUCCESS(f"Updated {pub.id}: {pub.title[:70]}"))
                ok += 1
            except Exception as exc:
                self.stderr.write(f"{pub.id}: {exc}")
                fail += 1
        self.stdout.write(f"Done. Success={ok}, failed={fail}")
