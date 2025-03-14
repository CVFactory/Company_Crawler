# File: ./company_crawler/company_crawler/spiders/company_spider.py
import scrapy
from company_crawler.items import CompanyItem

class CompanySpider(scrapy.Spider):
    name = "company_spider"
    start_urls = ["https://deepinsight.ninehire.site/"]

    def parse(self, response):
        try:
            # 기업 목록 페이지에서 링크 추출
            company_links = response.css("a.company-link::attr(href)").getall()
            if not company_links:
                self.logger.warning("No company links found on the page")
            for link in company_links:
                if not link.startswith(('http', 'https')):
                    link = response.urljoin(link)
                yield scrapy.Request(link, callback=self.parse_company)
        except Exception as e:
            self.logger.error(f"List page parsing failed: {response.url} (Status: {response.status})", exc_info=True)

    def parse_company(self, response):
        try:
            if response.status == 404:
                self.logger.warning(f"404 Error: {response.url}")
                return None
            item = CompanyItem()
            item['name'] = self._extract_text(response, "//h1[@class='company-name']/text()")
            item['url'] = response.url
            item['address'] = self._extract_text(response, "//div[@class='address']/text()")
            # 전체 텍스트 추출
            full_text = self._extract_full_text(response)
            item['full_text'] = full_text  # 새로운 필드 추가
            return item
        except Exception as e:
            self.logger.error(f"Detail page parsing failed: {response.url} (Status: {response.status})", exc_info=True)
            self.logger.debug(f"Response content: {response.text[:500]}")
            return None

    def _extract_text(self, response, xpath):
        text = response.xpath(xpath).get()
        return text.strip() if text and isinstance(text, str) else None

    def _extract_full_text(self, response):
        """
        웹페이지에서 모든 텍스트를 추출합니다.
        """
        # 스크립트와 스타일 태그를 제외한 텍스트 추출
        text_nodes = response.xpath("//body//*[not(self::script or self::style)]/text()").getall()
        cleaned_text = " ".join([text.strip() for text in text_nodes if text.strip()])
        return cleaned_text