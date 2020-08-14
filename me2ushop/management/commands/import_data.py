from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Import products in me2ushop'

    def handle(self, *args, **options):
        self.stdout.write("Importing products")
