import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from news_scraper.items import NewsScraperItem
from datetime import datetime
from urllib.parse import urljoin

class GoogleNewsSpider(scrapy.Spider):
    name = "google_news"

    def start_requests(self):
        """Use Selenium to load Google News homepage"""
        yield SeleniumRequest(
            url="https://news.google.com/",
            callback=self.parse,
            wait_time=5,  # Wait for JavaScript to load
            screenshot=True  # (Optional) Debugging
        )

    def parse(self, response):
        """Extract 'Top Stories' section dynamically using Selenium"""
        driver = response.meta["driver"]  # Get Selenium WebDriver

        # Wait for articles to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "WwrzSb"))
        )

        articles = driver.find_elements(By.CLASS_NAME, "WwrzSb")
        for article in articles:
            try:
                headline = article.text.strip()
                link = article.get_attribute("href")

                if headline and link:
                    item = NewsScraperItem()
                    item["caption"] = headline
                    item["article_url"] = urljoin("https://news.google.com", link)
                    item["scraped_at"] = datetime.utcnow()

                    yield item
            except Exception as e:
                self.logger.error(f"⚠️ Error extracting article: {e}")

