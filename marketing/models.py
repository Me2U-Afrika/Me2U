from django.urls import reverse
from django.utils import timezone
from django.db import models
from stdimage import StdImageField
from utils.models import CreationModificationDateMixin

# Create your models here.
from me2ushop.models import Product


class MarketingQueryset(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def bestselling(self):
        return self.filter(bestselling=True)

    def featured(self):
        return self.filter(featured=True).filter(start_date__lt=timezone.now()).filter(end_date__gte=timezone.now())


class MarketingManager(models.Manager):
    def get_queryset(self):
        return MarketingQueryset(self.model, using=self._db)

    def bestselling(self):
        return self.get_queryset().bestselling()

    def featured(self):
        return self.get_queryset().active().featured()

    def get_featured_item(self):
        try:
            return self.get_queryset().active().featured()[0]
        except:
            return None


class MarketingMessage(CreationModificationDateMixin):
    message = models.CharField(max_length=120)
    active = models.BooleanField(default=False)
    featured = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    end_date = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)

    objects = MarketingManager()

    class Meta:
        ordering = ['-start_date', '-end_date']

    def __str__(self):
        return str(self.message[:15])


# def slider_upload(instance, filename):
#     return 'images/marketing/slider/%s/%s' % (instance.id, filename)

class Slider(CreationModificationDateMixin):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)

    image = StdImageField(upload_to='images/marketing/slider', blank=True, null=True, variations={
        'slider_size': (520, 460),

    }, delete_orphans=True)
    image_url = models.CharField(max_length=250, null=True, blank=True)
    background_image_url = models.CharField(max_length=250, null=True, blank=True)
    link_url = models.CharField(max_length=250, null=True, blank=True)
    header_text = models.CharField(max_length=120, null=True, blank=True)
    text = models.CharField(max_length=120, null=True, blank=True)
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    end_date = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    banner_image = models.BooleanField(default=False)
    banner_background = models.BooleanField(default=False)

    objects = MarketingManager()

    class Meta:
        ordering = ['-start_date', '-end_date']

    def __str__(self):
        return str(self.header_text)


class Banner(CreationModificationDateMixin):
    image = StdImageField(upload_to='images/marketing/banner', blank=True, null=True, variations={
        'banner_size': (520, 460, True),

    }, delete_orphans=True)
    image_url = models.CharField(max_length=250, null=True, blank=True)
    link_url = models.CharField(max_length=250, null=True, blank=True)

    banner_text = models.CharField(max_length=200, null=True, blank=True)
    banner_header = models.CharField(max_length=120, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    banner_discount_price = models.DecimalField(max_digits=9, decimal_places=2)
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    bestselling = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    top_display = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    end_date = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    banner_image = models.BooleanField(default=False)
    banner_background = models.BooleanField(default=False)

    objects = MarketingManager()

    class Meta:
        ordering = ['-start_date', '-end_date']

    def __str__(self):
        return str(self.product.title)

    def get_absolute_url(self):
        return reverse('me2ushop:product', kwargs={'slug': self.product.slug})


class TrendInfo(CreationModificationDateMixin):
    trend_background = StdImageField(upload_to='images/marketing/trends', blank=True, null=True)
    trend_header = models.CharField(max_length=120)

    trend_text = models.TextField(max_length=300)

    def __str__(self):
        return str(self.trend_header)


class Trend(CreationModificationDateMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    start_date = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    end_date = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    active = models.BooleanField(default=True)

    objects = MarketingManager()

    class Meta:
        ordering = ['-start_date', '-end_date']

    def __str__(self):
        return str(self.product.title)

    def get_absolute_url(self):
        return reverse('me2ushop:product', kwargs={'slug': self.product.slug})


class Deals(CreationModificationDateMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    deal_discount_price = models.DecimalField(max_digits=9, decimal_places=2)
    is_featured = models.BooleanField(default=False, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    end_date = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)

    def __str__(self):
        return str(self.product.title)

    def get_absolute_url(self):
        return reverse('me2ushop:product', kwargs={'slug': self.product.slug})

    def total_items_ordered(self):
        orders = self.product.orderitem_set.all()
        total = 0
        for order_item in orders:
            if order_item.ordered:
                total += order_item.quantity

        return total


class MarketingEmails(CreationModificationDateMixin):
    email = models.EmailField()
    subscribed = models.BooleanField(default=True)

    def __str__(self):
        return str(self.email)
