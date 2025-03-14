# File: ./myapp/models.py
from django.core.exceptions import ValidationError
from django.db import models

def validate_url_format(value):
    """
    URL 형식 검증 함수
    """
    if not value.startswith(('http://', 'https://')):
        raise ValidationError('URL은 http:// 또는 https://로 시작해야 합니다.')

class Company(models.Model):
    full_text = models.TextField(verbose_name="전체 텍스트")  # 새로운 필드 추가