# File: ./myapp/views.py
from django.shortcuts import render
from django.views.generic import ListView
from myapp.models import Company
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from myapp.serializers import CompanySerializer
import logging

logger = logging.getLogger(__name__)

class CompanyListView(ListView):
    model = Company
    template_name = "company_list.html"  # 템플릿 파일 이름
    context_object_name = "companies"

    def get_queryset(self):
        try:
            return Company.objects.all().order_by("-id")  # 최신 데이터 우선 정렬
        except Exception as e:
            logger.error(f"Error fetching companies: {str(e)}", exc_info=True)
            return Company.objects.none()  # 빈 쿼리셋 반환

@api_view(['GET'])
def company_api(request):
    try:
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"API error: {str(e)}", exc_info=True)
        return Response({"error": "Internal server error"}, status=500)