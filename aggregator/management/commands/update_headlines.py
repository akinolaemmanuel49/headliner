from django.core.management.base import BaseCommand
from django.core.cache import cache

from utils.headliner import bbcnews_headlines, nbcnews_headlines, headlines


class Command(BaseCommand):
    help = "Fetch and update the latest headlines from sources"

    def handle(self, *args, **options):
        headlines([bbcnews_headlines(), nbcnews_headlines()])

        self.stdout.write(self.style.SUCCESS("Headlines updated successfully!"))
