import itertools

from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from mptt.models import MPTTModel
from stdimage import StdImageField

from me2ushop.models import Product
from utils.models import CreationModificationDateMixin
from django.conf import settings
from ckeditor.fields import RichTextField


# Create your models here.

class Post(CreationModificationDateMixin):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,
                            default='',
                            editable=False,
                            max_length=255,
                            )
    # content = models.TextField()
    content = RichTextUploadingField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = StdImageField(blank=True, null=True, upload_to='images/products', help_text="upload blog cover Image",
                          variations={
                              'medium': (500, 460),
                              'large': (800, 460),

                          }, delete_orphans=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='post_likes')
    snippet = models.CharField(max_length=350, default='Click Below To Read Blog Post...',
                               help_text='This is what USERS/READERS who have NOT SIGNED in will see. Make them login '
                                         'to read your article by capturing their attention. What is your post about')

    def __str__(self):
        return str(self.title)

    def get_total_likes(self):
        return self.likes.count()

    def cross_reads(self):
        # orders = Order.objects.filter(items__item=self)
        # order_items = OrderItem.objects.filter(order__in=orders).exclude(item=self)
        posts = Post.objects.all().exclude(slug=self.slug)
        return posts

    def get_absolute_url(self):

        return reverse('blog:postView', kwargs={'slug': self.slug})

    def _generate_slug(self):
        max_length = self._meta.get_field('slug').max_length
        value = self.title
        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not Post.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)

        return slug_candidate

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = self._generate_slug()

        super().save(*args, **kwargs)


class Comment(CreationModificationDateMixin):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField()

    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'Comments'

    def __str__(self):
        return '%s - %s' % (self.post.title, self.user)
