from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def crawl(start_url, output_file="crawled_results.txt"):
    # 크롬 드라이버 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    
    # 최신 Selenium은 자동으로 Chrome 드라이버를 관리 (Service 불필요)
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 1차 크롤링: 시작 URL
        print(f"1차 크롤링: {start_url}")
        driver.get(start_url)
        
        # 텍스트 추출
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        main_text = soup.get_text(separator=" ", strip=True)
        
        # 링크 추출
        elements = driver.find_elements(By.TAG_NAME, "a")
        all_links = [elem.get_attribute("href") for elem in elements if elem.get_attribute("href")]
        
        # 같은 도메인 링크만 필터링
        base_domain = urlparse(start_url).netloc
        valid_links = []
        for link in all_links:
            if link and link.startswith('http'):
                link_domain = urlparse(link).netloc
                if link_domain == base_domain:
                    valid_links.append(link)
        
        # 중복 제거
        links = list(dict.fromkeys(valid_links))
        
        # 결과 저장
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"=== 1차 크롤링: {start_url} ===\n{main_text}\n\n")
            f.write(f"발견된 링크 수: {len(links)}\n\n")
        
        # 2차 크롤링
        print(f"2차 크롤링: {len(links)}개 링크")
        
        for i, link in enumerate(links):
            try:
                print(f"링크 {i+1}/{len(links)}: {link}")
                driver.get(link)
                
                # 텍스트 추출
                soup = BeautifulSoup(driver.page_source, "html.parser")
                for script in soup(["script", "style"]):
                    script.extract()
                sub_text = soup.get_text(separator=" ", strip=True)
                
                # 결과 저장
                with open(output_file, "a", encoding="utf-8") as f:
                    f.write(f"=== 2차 크롤링 ({i+1}/{len(links)}): {link} ===\n{sub_text}\n\n")
            
            except Exception as e:
                print(f"오류 ({link}): {e}")
        
        print("크롤링 완료")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    target_url = "https://deepinsight.ninehire.site/"
    crawl(target_url) 