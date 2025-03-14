import scrapy

class CompanyItem(scrapy.Item):
    full_text = scrapy.Field()  # 전체 텍스트 필드

    def validate(self):
        """
        데이터 유효성 검사
        """
        if not self.get('full_text'):
            raise ValueError("Missing required field: full_text")
        return True