import os
import requests
import pymongo
import hashlib
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Setup logging
logging.basicConfig(
    filename="news_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["google_news_database"]
articles_collection = db["news_articles"]
images_collection = db["news_images"]

# Set up for Chrome driver with headless mode
options = Options()
options.add_argument("--headless")  #  headless mode to save resources
driver = webdriver.Chrome(options=options)

def generate_hash(headline, link):
    """Generate a unique hash based on headline and link to prevent duplication."""
    return hashlib.sha256(f"{headline}{link}".encode()).hexdigest()

def scrape_google_news():
    try:
        logging.info("Starting Google News Scraper")
        driver.get("https://news.google.com/home?hl=en-IN&gl=IN&ceid=IN:en")

        # Wait for the "Top stories" link to load and find it
        wait = WebDriverWait(driver, 15)
        top_stories_link = wait.until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Top stories')]")
        ))

        top_stories_url = top_stories_link.get_attribute("href")
        logging.info(f"Navigating to Top stories: {top_stories_url}")
        driver.get(top_stories_url)

        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))
        articles = driver.find_elements(By.TAG_NAME, "article")

        for article in articles:
            try:
                headline_element = article.find_element(By.XPATH, ".//a[@class='gPFEn']")
                headline = headline_element.text.strip()
                link = headline_element.get_attribute("href")
                scrape_timestamp = datetime.utcnow()

                article_hash = generate_hash(headline, link)
                if articles_collection.find_one({"hash": article_hash}):
                    logging.info(f"Skipping duplicate article: {headline}")
                    continue

                figure_element = article.find_element(By.XPATH, ".//figure[contains(@class, 'P22Vib')]")
                image_element = figure_element.find_element(By.TAG_NAME, "img")
                image_url = image_element.get_attribute("src")

                response = requests.get(image_url, stream=True)
                image_binary = response.content if response.status_code == 200 else None

                if image_binary:
                    image_record = {"image": image_binary, "image_url": image_url}
                    image_id = images_collection.insert_one(image_record).inserted_id
                else:
                    image_id = None

                article_data = {
                    "headline": headline,
                    "link": link,
                    "scrape_timestamp": scrape_timestamp,
                    "image_id": image_id,
                    "hash": article_hash
                }
                articles_collection.insert_one(article_data)
                logging.info(f"Saved article: {headline}")
            except Exception as e:
                logging.error(f"Error processing article: {e}")
                continue
    except Exception as e:
        logging.critical(f"Fatal error in scraper: {e}")
    finally:
        driver.quit()
        logging.info("Google News Scraper finished execution.")

if __name__ == "__main__":
    scrape_google_news()
