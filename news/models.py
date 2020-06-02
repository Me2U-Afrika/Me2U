from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Addicts(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    age = models.IntegerField()
    location = models.CharField(max_length=255)
    availability = models.BooleanField()
    image_url = models.CharField(max_length=2083)
    description = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # addicts_image = models.ImageField(upload_to='')


    def __str__(self):
        return self.name, self.age, self.availability
#
#
# class Referrals(models.Model):
#     link = models.CharField(max_length=2083)
#     description = models.CharField(max_length=255)
#     discount = models.FloatField()
#
#
# class ads(models.Model):
#     ad_type = models.CharField(max_length=60)
#     ad_description = models.TextField()
#     ad_requirements = models.CharField(max_length=255)
#     # date_posted = models.DateTimeField(default=timezone.now)
#     # Addicts = models.ForeignKey(Addicts)
#
#
# class tags(models.Model):
#     name = models.CharField(max_length=30)
#
#     def __str__(self):
#         return self.name
