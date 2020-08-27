from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from rest_framework.authtoken.models import Token

from .models import ProductImage, Order, OrderItem
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def orderitem_to_order_status(sender, instance, **kwargs):
    if not instance.order.items.filter(status__lt=OrderItem.SENT).exists():
        logger.info(
            "All items for order %d have been processed. Marking as done.",
            instance.order.id,
        )
        instance.order.status = Order.DONE
        instance.order.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        token = Token.objects.create(user=instance)
    return token