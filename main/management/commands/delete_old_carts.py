from main import cart
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Delete shopping cart item mor than 90 days old"

    def handle(self, *args, **options):
        cart.remove_old_cart_items()
