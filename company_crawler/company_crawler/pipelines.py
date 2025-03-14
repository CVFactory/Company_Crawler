# File: ./company_crawler/company_crawler/pipelines.py
import logging
from scrapy.exceptions import DropItem
from myapp.models import Company
from django.db import transaction, IntegrityError, DatabaseError, OperationalError
from scrapy import signals

logger = logging.getLogger(__name__)

class SaveToDatabasePipeline:
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.handle_spider_error, signal=signals.spider_error)
        crawler.signals.connect(pipeline.handle_item_dropped, signal=signals.item_dropped)
        return pipeline

    def process_item(self, item, spider):
        try:
            item.validate()  # 유효성 검사
            with transaction.atomic():
                company, created = Company.objects.get_or_create(
                    name=item['name'],
                    defaults={
                        'url': item['url'],
                        'address': item['address'],
                        'full_text': item.get('full_text', '')  # 새로운 필드 추가
                    }
                )
                if not created:
                    # 중복 데이터가 발견된 경우 갱신
                    company.url = item['url']
                    company.address = item['address']
                    company.full_text = item.get('full_text', '')
                    company.save()
                    spider.logger.warning(f"Updated duplicate entry: {item['name']} (URL: {item['url']})")
                spider.logger.debug(f"Successfully processed: {item['name']} (ID: {company.id})")
            return item
        except IntegrityError as e:
            error_msg = f"Integrity error for {item.get('name', 'N/A')}: {str(e)}"
            spider.logger.error(error_msg, exc_info=True)
            raise DropItem(error_msg)
        except OperationalError as e:
            error_msg = f"Database operational error: {str(e)}"
            spider.logger.critical(error_msg, exc_info=True)
            spider.crawler.engine.pause()
            raise DropItem(error_msg)
        except DatabaseError as e:
            error_msg = f"Database connection error: {str(e)}"
            spider.logger.error(error_msg, extra={'item_data': dict(item)})
            raise DropItem(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error processing {item.get('name', 'N/A')}: {str(e)}"
            spider.logger.exception(error_msg, exc_info=True)
            raise DropItem(error_msg)

    def handle_spider_error(self, failure, response, spider):
        error_data = {
            'url': response.url,
            'status': response.status,
            'response_excerpt': response.text[:500] if response else 'N/A',
            'traceback': failure.getErrorMessage(),
        }
        spider.logger.error(f"Spider error occurred: {error_data}")

    def handle_item_dropped(self, item, response, spider, exception):
        spider.logger.warning(f"Dropped item: {dict(item)}. Reason: {str(exception)}")