from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models

def validate_url_format(value):
    if not value.startswith(('http://', 'https://')):
        raise ValidationError(_('Invalid URL format. Must start with http/https'))

class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="기업 이름")
    url = models.URLField(verbose_name="웹사이트 URL")  # validators 제거
    address = models.TextField(blank=True, null=True, verbose_name="주소")
    full_text = models.TextField(blank=True, null=True, verbose_name="전체 텍스트")  # 새로운 필드 추가

    def clean(self):
        super().clean()  # 중복 검증 제거