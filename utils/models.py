from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now as timezone_now


# Create your models here.

class CreationModificationDateMixin(models.Model):
    """  Abstract base class with a creation and modification  date and time  """
    created = models.DateTimeField(
        _("creation date and time"),
        editable=False
    )
    modified = models.DateTimeField(
        _("modification date and time"),
        null=True,
        editable=False,
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            # print('true we came to create')
            # print('true we came to create', self.created)

            self.created = timezone_now()

        else:
            # print('true we came to modify')
            # self.created = timezone_now()
            self.modified = timezone_now()

            super(CreationModificationDateMixin, self).save(*args, **kwargs)

        super(CreationModificationDateMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True
