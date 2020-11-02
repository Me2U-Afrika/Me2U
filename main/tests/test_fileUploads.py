from io import StringIO
import tempfile
from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings
from me2ushop import models
from categories.models import Category, Department


class TestImport(TestCase):
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_import_data(self):
        out = StringIO()
        args = ['categories/fixtures/products.csv',
                'media/images/Electronics']
        call_command('import_data', *args, stdout=out)
        expected_out = ('importing products\n'
                        'Categories processed=0 (created=0)\n'
                        'Products processed=3 (created=3)\n'
                        'Images processed=3\n')

        self.assertEqual(out.getvalue(), expected_out)
        self.assertEqual(models.Product.objects.count(), 3)
        self.assertEqual(models.ProductImage.objects.count(), 3)
        self.assertEqual(Department.objects.count(), 6)
