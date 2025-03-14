# File: ./company_crawler/company_crawler/items.py
import scrapy

class CompanyItem(scrapy.Item):
    name = scrapy.Field()          # 기업 이름 필드
    url = scrapy.Field()           # 기업 URL 필드
    address = scrapy.Field()       # 기업 주소 필드
    full_text = scrapy.Field()     # 전체 텍스트 필드

    def validate(self):
        """
        데이터 유효성 검사
        """
        required_fields = ['name', 'url']
        for field in required_fields:
            if not self.get(field):
                error_msg = f"Missing required field: {field}"
                raise ValueError(error_msg)
        # URL 형식 검증 추가
        if 'url' in self and not self['url'].startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL format: {self['url']}")
        return True