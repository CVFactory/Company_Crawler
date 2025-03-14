# File: ./myproject/urls.py
from django.contrib import admin
from django.urls import path
from myapp.views import CompanyListView, company_api  # company_api 추가

urlpatterns = [
    path("admin/", admin.site.urls),
    path("companies/", CompanyListView.as_view(), name="company-list"),  # 기업 목록 페이지
    path("api/companies/", company_api, name="company-api"),  # API 엔드포인트 추가
]