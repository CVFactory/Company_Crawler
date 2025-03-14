# File: ./myapp/tests.py
from django.test import TestCase
from myapp.models import Company

class CompanyModelTest(TestCase):
    def test_full_text_validation(self):
        company = Company(full_text="")
        with self.assertRaises(ValueError) as cm:
            company.full_clean()
        self.assertIn('full_text', cm.exception.error_dict)