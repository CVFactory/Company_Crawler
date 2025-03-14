# File: ./myapp/admin.py
from django.contrib import admin
from myapp.models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('full_text',)
    search_fields = ('full_text',)