import scrapy
from company_crawler.items import CompanyItem

class CompanySpider(scrapy.Spider):
    name = "company_spider"
    # 특정 기업의 세부 페이지 URL을 직접 지정
    start_urls = [
        "https://deepinsight.ninehire.site/"
    ]

    def parse(self, response):
        """
        웹페이지에서 모든 텍스트를 추출하고 저장합니다.
        """
        try:
            # CompanyItem 객체 생성
            item = CompanyItem()
            # 전체 텍스트 추출
            full_text = self._extract_full_text(response)
            item['full_text'] = full_text
            yield item
        except Exception as e:
            self.logger.error(f"Error extracting text from: {response.url}", exc_info=True)

    def _extract_full_text(self, response):
        """
        웹페이지에서 모든 텍스트를 추출합니다.
        """
        # 스크립트와 스타일 태그를 제외한 텍스트 추출
        text_nodes = response.xpath("//body//*[not(self::script or self::style)]/text()").getall()
        cleaned_text = " ".join([text.strip() for text in text_nodes if text.strip()])
        return cleaned_text