import os
import requests
import pymongo
import hashlib
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["news_database"]
articles_collection = db["news_articles"]
images_collection = db["news_images"]

# Set up for Chrome driver with headless mode
options = Options()
options.add_argument("--headless")  # headless mode to save resources
driver = webdriver.Chrome(options=options)

def generate_hash(headline, link):
    """Generate a unique hash based on headline and link to prevent duplication."""
    return hashlib.sha256(f"{headline}{link}".encode()).hexdigest()

try:
    # Step 1: Open the Google News homepage
    driver.get("https://news.google.com/home?hl=en-IN&gl=IN&ceid=IN:en")

    # Step 2: Wait for the "Top stories" link to load and find it
    wait = WebDriverWait(driver, 10)
    top_stories_link = wait.until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Top stories')]")
    ))

    # Step 3: Get the link to "Top stories"
    top_stories_url = top_stories_link.get_attribute("href")
    print(f"Navigating to Top stories: {top_stories_url}\n")

    # Step 4: Navigate to the "Top stories" page
    driver.get(top_stories_url)

    # Step 5: Wait for the page to load
    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))

    # Step 6: Locate and extract all headlines, links, and images
    articles = driver.find_elements(By.TAG_NAME, "article")

    for article in articles:
        try:
            # Extracting headline and its link
            headline_element = article.find_element(By.XPATH, ".//a[@class='gPFEn']")
            headline = headline_element.text.strip()
            link = headline_element.get_attribute("href")
            scrape_timestamp = datetime.utcnow()

            # Generating a unique hash for de-duplication
            article_hash = generate_hash(headline, link)

            #//////////////////////////////////////////////////

            # Checking if the article already exists

            #/////////////////////////////////////////////////////////
            if articles_collection.find_one({"hash": article_hash}):
                print(f"Skipping duplicate article: {headline}")
                continue

            # Extracting the image link only if it is inside a <figure> tag
            # by doing this we get rid of small logos and other unwanted images as those come under <img> 

            figure_element = article.find_element(By.XPATH, ".//figure[contains(@class, 'P22Vib')]")
            image_element = figure_element.find_element(By.TAG_NAME, "img")
            image_url = image_element.get_attribute("src")

            # Downloading the image as binary data
            response = requests.get(image_url, stream=True)
            image_binary = response.content if response.status_code == 200 else None

            # Inserting image data into MongoDB and geting the inserted ID
            if image_binary:
                image_record = {"image": image_binary, "image_url": image_url}
                image_id = images_collection.insert_one(image_record).inserted_id
            else:
                image_id = None

            # Inserting article metadata into MongoDB
            article_data = {
                "headline": headline,
                "link": link,
                "scrape_timestamp": scrape_timestamp,
                "image_id": image_id,
                "hash": article_hash  # Store unique hash for de-duplication
            }
            articles_collection.insert_one(article_data)

            print(f"Saved to MongoDB: {headline}")

        except Exception as e:
            # Skipping articles missing required elements or <figure> tags
            continue

finally:
    # Step 7: Closing the browser
    driver.quit()
    print("Data saved to MongoDB successfully.")
