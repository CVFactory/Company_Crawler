# File: ./myapp/tests.py
from django.test import TestCase
from myapp.models import Company

class CompanyModelTest(TestCase):
    def test_url_validation(self):
        company = Company(name="Test", url="invalid-url")
        with self.assertRaises(ValidationError) as cm:
            company.clean_fields()
        self.assertIn('url', cm.exception.error_dict)