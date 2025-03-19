from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urlparse, urlunparse, urldefrag, parse_qs
from bs4 import BeautifulSoup
from collections import deque
import logging
import re

# 로그 설정 (DEBUG 레벨, 파일만 기록)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("crawler.log")]
)

# Chrome 옵션 설정
def set_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")  # 백그라운드 실행
    return chrome_options

# WebDriver 생성
def create_driver():
    chromedriver_path = "C:\\chromedriver-win64\\chromedriver.exe"
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=set_chrome_options())
    return driver

# URL 정규화 (쿼리 및 프래그먼트 제거)
def normalize_url(url):
    parsed = urlparse(url)
    # 쿼리 파라미터와 프래그먼트 제거
    normalized = parsed._replace(query="", fragment="")
    return urlunparse(normalized)

# 하위 페이지 여부 확인 (프로토콜 및 경로 검증 강화)
def is_subpage(link, base_url):
    try:
        parsed_link = urlparse(link)
        parsed_base = urlparse(base_url)
        
        # http/https 프로토콜만 허용
        if parsed_link.scheme not in ["http", "https"]:
            return False
        
        # 도메인, 경로 검증
        return (parsed_link.netloc == parsed_base.netloc and
                parsed_link.path.startswith(parsed_base.path))
    except Exception as e:
        logging.error(f"URL 검증 오류 ({link}): {e}")
        return False

# 페이지 텍스트 정규화 (공백 및 특수 문자 처리)
def normalize_text(text):
    # 연속 공백 제거 및 줄바꿈 통일
    return re.sub(r'\s+', ' ', text).strip()

# 페이지 텍스트 추출
def extract_text_from_page(driver):
    try:
        # 동적 콘텐츠 로딩 대기 (예: 본문 요소)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return normalize_text(text)
    except Exception as e:
        logging.error(f"텍스트 추출 실패: {e}")
        return ""

# BFS 기반 깊이 제한 크롤링
def crawl_with_depth_limit(start_url, output_file="crawled_texts.txt", max_depth=2):
    visited = set()
    queue = deque([(start_url, 0)])
    driver = create_driver()

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            while queue:
                url, depth = queue.popleft()
                normalized_url = normalize_url(url)
                
                # 방문 이력 또는 깊이 초과 시 건너뜀
                if normalized_url in visited or depth > max_depth:
                    logging.debug(f"Skip {normalized_url} (Depth: {depth})")
                    continue
                visited.add(normalized_url)

                try:
                    logging.info(f"Processing {url} (Depth: {depth})")
                    driver.get(url)
                    
                    # 텍스트 추출 및 저장
                    text = extract_text_from_page(driver)
                    f.write(f"=== Depth {depth}: {url} ===\n{text}\n\n")

                    # 최대 깊이에 도달하지 않았을 때만 하위 페이지 추출
                    if depth < max_depth:
                        elements = driver.find_elements(By.TAG_NAME, "a")
                        links = [elem.get_attribute("href") for elem in elements if elem.get_attribute("href")]
                        unique_links = list(dict.fromkeys(links))  # 중복 제거
                        subpages = [link for link in unique_links if is_subpage(link, start_url)]

                        for subpage in subpages:
                            if subpage not in visited:
                                queue.append((subpage, depth + 1))
                                logging.debug(f"Added subpage to queue: {subpage} (Next Depth: {depth + 1})")

                except TimeoutException:
                    logging.error(f"Timeout on {url}")
                except Exception as e:
                    logging.error(f"Error processing {url}: {e}")

    finally:
        driver.quit()
        logging.info("Crawling completed.")

# 메인 실행
if __name__ == "__main__":
    start_url = "https://www.samsungcareers.com/"
    output_file = "crawled_texts.txt"
    crawl_with_depth_limit(start_url, output_file, max_depth=2)