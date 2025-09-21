from django.core.management.base import BaseCommand

from interest.service import InterestService


class Command(BaseCommand):

    def handle(self, *args, **options):
        service = InterestService()

        r = service.get_requests(phrase='Cute cats')
        pass