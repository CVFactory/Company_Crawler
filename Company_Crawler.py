from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urlparse, urlunparse, urldefrag
from bs4 import BeautifulSoup
from collections import deque
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import html  # HTML 엔티티 처리 추가
import threading
from concurrent.futures import wait  # 추가된 임포트

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

# WebDriver 풀 관리 (스레드 로컬 스토리지 사용)
_thread_local = threading.local()

def get_driver():
    if not hasattr(_thread_local, "driver"):
        chromedriver_path = "C:\\chromedriver-win64\\chromedriver.exe"
        service = Service(chromedriver_path)
        _thread_local.driver = webdriver.Chrome(service=service, options=set_chrome_options())
    return _thread_local.driver

# WebDriver 종료
def quit_driver():
    if hasattr(_thread_local, "driver"):
        _thread_local.driver.quit()
        delattr(_thread_local, "driver")

# URL 정규화 (쿼리 및 프래그먼트 제거)
def normalize_url(url):
    parsed = urlparse(url)
    normalized = parsed._replace(query="", fragment="")
    return urlunparse(normalized)

# 유효한 URL인지 검증 (로그인/회원가입 페이지 제외)
def is_valid_url(url):
    parsed = urlparse(url)
    invalid_paths = ["/login", "/signup", "/logout", "/account"]
    return (parsed.scheme in ["http", "https"] and
            not any(parsed.path.startswith(path) for path in invalid_paths))

# 하위 페이지 여부 확인 (쿼리/프래그먼트 제거 추가)
def is_subpage(link, base_url):
    try:
        parsed_link = urlparse(link)
        parsed_base = urlparse(base_url)
        if not is_valid_url(link):
            return False
        return (parsed_link.netloc == parsed_base.netloc and
                parsed_link.path.startswith(parsed_base.path) and
                not parsed_link.query and not parsed_link.fragment)
    except Exception as e:
        logging.error(f"URL 검증 오류 ({link}): {e}")
        return False

# 텍스트 줄바꿈 추가 (70자마다 줄바꿈)
def wrap_text(text, max_length=70):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_length:
            current_line += (" " + word if current_line else word)
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)

# 페이지 텍스트 정규화 (HTML 엔티티 처리 추가)
def normalize_text(text):
    text = html.unescape(text)  # HTML 엔티티 디코딩 추가
    return re.sub(r'\s+', ' ', text).strip()

# 페이지 텍스트 추출 (예외 처리 강화)
def extract_text_from_page(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return normalize_text(text)
    except TimeoutException:
        logging.error("페이지 로딩 시간 초과")
        return ""
    except Exception as e:
        logging.error(f"텍스트 추출 실패: {e}")
        return ""

# 병렬 처리를 위한 페이지 처리 함수 (WebDriver 재사용)
def process_page(url, depth):
    driver = get_driver()
    try:
        driver.get(url)
        text = extract_text_from_page(driver)
        return url, depth, text
    except TimeoutException:
        logging.error(f"Timeout: {url}")
        return url, depth, None
    except Exception as e:
        logging.error(f"페이지 처리 실패 ({url}): {e}")
        return url, depth, None

# BFS 기반 깊이 제한 크롤링 (병렬 처리 개선)
def crawl_with_depth_limit(start_url, output_file="crawled_texts.txt", max_depth=2, max_workers=5):
    visited = set()
    queue = deque([(start_url, 0)])
    
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            
            while queue or futures:
                # 큐에 남은 작업이 있으면 스레드 풀에 제출
                while queue and len(futures) < max_workers:
                    url, depth = queue.popleft()
                    normalized_url = normalize_url(url)
                    
                    if normalized_url in visited or depth > max_depth:
                        logging.debug(f"Skip {normalized_url} (Depth: {depth})")
                        continue
                    visited.add(normalized_url)
                    
                    future = executor.submit(process_page, url, depth)
                    futures[future] = (url, depth)
                    logging.info(f"Submitted {url} (Depth: {depth}) for processing")

                # 완료된 작업 처리
                done, _ = wait(futures.keys(), timeout=0.1)
                for future in done:
                    url, depth = futures.pop(future)
                    try:
                        result_url, result_depth, text = future.result()
                        if text:
                            wrapped_text = wrap_text(text, max_length=70)
                            with open(output_file, "a", encoding="utf-8") as f:
                                f.write(f"=== Depth {result_depth}: {result_url} ===\n{wrapped_text}\n\n")
                            logging.info(f"Saved text from {result_url} (Depth: {result_depth})")
                        
                        # 하위 페이지 추출 (최대 깊이 미만인 경우)
                        if result_depth < max_depth:
                            driver = get_driver()
                            try:
                                driver.get(url)
                                elements = driver.find_elements(By.TAG_NAME, "a")
                                links = [elem.get_attribute("href") for elem in elements if elem.get_attribute("href")]
                                unique_links = list(dict.fromkeys(links))  # 중복 제거
                                subpages = [link for link in unique_links if is_subpage(link, start_url)]
                                
                                for subpage in subpages:
                                    normalized_subpage = normalize_url(subpage)
                                    if normalized_subpage not in visited:
                                        queue.append((subpage, result_depth + 1))
                                        logging.debug(f"Added subpage to queue: {subpage} (Next Depth: {result_depth + 1})")
                            except Exception as e:
                                logging.error(f"하위 페이지 추출 실패 ({url}): {e}")
                    except Exception as e:
                        logging.error(f"작업 처리 실패 ({url}): {e}")
    finally:
        # 모든 WebDriver 종료
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(quit_driver).result()
        executor.shutdown()

# 메인 실행
if __name__ == "__main__":
    start_url = "https://www.samsungcareers.com/"
    output_file = "crawled_texts.txt"
    crawl_with_depth_limit(start_url, output_file, max_depth=2, max_workers=5)