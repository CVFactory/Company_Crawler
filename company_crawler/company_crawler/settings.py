import sys
import os
import django

# Django 프로젝트 경로 설정
sys.path.append('D:\\Coding\\Django')  # Scrapy 프로젝트의 부모 디렉토리 추가
sys.path.append('D:\\Coding\\Django\\myproject')  # Django 프로젝트 경로
os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'  # Django 설정 모듈
django.setup()

# Scrapy 기본 설정
BOT_NAME = 'company_crawler'

SPIDER_MODULES = ['company_crawler.spiders']  # 스파이더 디렉토리
NEWSPIDER_MODULE = 'company_crawler.spiders'

# 요청 간격 및 동시성 제어
CONCURRENT_REQUESTS = 32  # 동시에 처리할 요청 수
DOWNLOAD_DELAY = 1  # 서버 부하 방지를 위한 딜레이
DOWNLOAD_TIMEOUT = 30  # 요청 시간 초과 설정

# 재시도 설정
RETRY_ENABLED = True
RETRY_TIMES = 3  # 실패 시 재시도 횟수
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]  # 재시도 HTTP 코드 추가
RETRY_PRIORITY_ADJUST = -1

# User-Agent 회전 (차단 방지)
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
}

# IP 차단 방지를 위한 프록시 미들웨어 추가 (옵션)
# DOWNLOADER_MIDDLEWARES.update({
#     'scrapy_proxy_pool.middlewares.ProxyPoolMiddleware': 610,
#     'scrapy_proxy_pool.middlewares.BanDetectionMiddleware': 620,
# })

# Proxy Pool 설정 (필요 시)
PROXY_POOL_ENABLED = True
PROXY_POOL_FORCE_REFRESH = True
PROXY_POOL_PAGE_RETRY_TIMES = 3

# robots.txt 준수 설정 추가
ROBOTSTXT_OBEY = True

# 파이프라인 활성화
ITEM_PIPELINES = {
    'company_crawler.pipelines.SaveToDatabasePipeline': 300,  # 데이터 저장 파이프라인
}

# 로깅 설정
LOG_FILE = 'crawler.log'
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s (%(filename)s:%(lineno)d)'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FILE_APPEND = False  # 새로운 크롤링 시작 시 로그 파일 덮어쓰기

# 지원할 브라우저 유형 지정 (예: Chrome, Firefox, Safari, Edge)
USER_AGENTS_ALLOWED_BROWSERS = [
    "Chrome",
    "Firefox",
    "Safari",
    "Edge",
]

# 지원할 장치 유형 지정 (예: Desktop)
USER_AGENTS_ALLOWED_DEVICES = [
    "Desktop",
]

# 지원하지 않는 유형을 선택할 경우 에러 대신 무시
USER_AGENTS_WARN_ON_UNSUPPORTED = False