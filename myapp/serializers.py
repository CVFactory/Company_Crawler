# File: ./myapp/serializers.py
from rest_framework import serializers
from myapp.models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'  # 모든 필드를 포함하거나 특정 필드만 지정 가능