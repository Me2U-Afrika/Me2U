from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from me2ushop.models import Product, ProductImage, RequestRefund
from .models import Profile, User, EmailConfirmed
import random
import hashlib
import codecs


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    user = instance
    if created:
        Profile.objects.create(user=user)
        Token.objects.create(user=user)

        email_confirmed, email_created = EmailConfirmed.objects.get_or_create(user=user)
        # if email_created:
        #     short_hash = hashlib.sha1(codecs.encode(str(random.random()))).hexdigest()[:5]
        #     # print(user.username)
        #     username = user.username
        #     activation_key = hashlib.sha1(codecs.encode(short_hash + username)).hexdigest()
        #     email_confirmed.activationKey = activation_key
        #     email_confirmed.save()
        #     email_confirmed.activate_user_email()


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=Product)
def save_product(sender, instance, **kwargs):
    for category in instance.product_categories.all():
        category.save()


#
@receiver(post_save, sender=ProductImage)
def save_image(sender, instance, **kwargs):
    if instance.in_display:
        if not instance.item.is_active:
            # print('we came to set it active')
            instance.item.is_active = True
    instance.item.save()


@receiver(post_save, sender=RequestRefund)
def save_refund(sender, instance, **kwargs):
    if instance.accepted:
        instance.order.refund_granted = True
    elif not instance.accepted:
        instance.order.refund_granted = False
