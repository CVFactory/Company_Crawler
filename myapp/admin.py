from django.contrib import admin
from myapp.models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'address')
    search_fields = ('name', 'url')