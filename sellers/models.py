from django.db import models
from stdimage import StdImageField
from users.models import User


class Sellers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = StdImageField(upload_to='images/profile_pics/sellers', blank=True, null=True, default='default.svg',
                          variations={
                              'thumbnail': (300, 300)}, delete_orphans=True)
    email = models.EmailField(max_length=50)

class BusinessInformation(models.Model):
    owner = models.ForeignKey(Sellers, on_delete=models.CASCADE)
    # business_type = models.


