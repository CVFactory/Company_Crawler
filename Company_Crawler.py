from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import deque
import logging

# 로그 설정 (터미널 출력 제거)
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG 레벨로 설정
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("crawler.log")]  # StreamHandler 제거
)

# Chrome 옵션 설정
def set_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")  # 백그라운드 실행 (필요 시 주석 해제)
    return chrome_options

# WebDriver 생성
def create_driver():
    chromedriver_path = "C:\\chromedriver-win64\\chromedriver.exe"
    service = Service(chromedriver_path)
    logging.debug("Initializing Chrome WebDriver...")
    driver = webdriver.Chrome(service=service, options=set_chrome_options())
    return driver

# 하위 페이지 여부 확인
def is_subpage(link, base_url):
    try:
        parsed_link = urlparse(link)
        parsed_base = urlparse(base_url)
        result = (parsed_link.netloc == parsed_base.netloc and
                  parsed_link.scheme == parsed_base.scheme and
                  parsed_link.path.startswith(parsed_base.path))
        logging.debug(f"is_subpage({link}, {base_url}) -> {result}")
        return result
    except Exception as e:
        logging.error(f"Error in is_subpage: {e}")
        return False

# 페이지 텍스트 추출
def extract_text_from_page(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    logging.debug(f"Extracted text. Length: {len(text)} characters.")
    return text

# BFS 기반 깊이 제한 크롤링
def crawl_with_depth_limit(start_url, output_file="output.txt", max_depth=2):
    visited = set()
    queue = deque([(start_url, 0)])  # (URL, 깊이)
    driver = create_driver()

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            while queue:
                url, depth = queue.popleft()
                if url in visited or depth > max_depth:
                    logging.debug(f"Skipping already visited or exceeded depth: {url}")
                    continue
                visited.add(url)

                try:
                    logging.debug(f"Navigating to URL: {url}")
                    driver.get(url)
                    driver.implicitly_wait(5)
                    logging.info(f"Processing {url} (Depth: {depth})")

                    # 텍스트 추출 및 저장
                    text = extract_text_from_page(driver)
                    f.write(f"=== Depth {depth}: {url} ===\n{text}\n\n")

                    # 최대 깊이에 도달하지 않았을 때만 하위 페이지 추출
                    if depth < max_depth:
                        logging.debug(f"Finding <a> tags on {url}...")
                        elements = driver.find_elements(By.TAG_NAME, "a")
                        links = [elem.get_attribute("href") for elem in elements if elem.get_attribute("href")]
                        logging.debug(f"Found {len(links)} <a> tags on the page.")

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