from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'


    def handle(self, *args, **options):
        call_command('loaddata', 'initial-data.json')
        call_command('loaddata', 'approval-sections.json')
