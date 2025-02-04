import os
import csv
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Directory to save images
IMAGE_DIR = "news_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# CSV file path
CSV_FILE = "news_data.csv"

# Setting up Chrome driver with headless mode
options = Options()
options.add_argument("--headless")  # headless mode to save resources
driver = webdriver.Chrome(options=options)

try:
    # Step 1: Opening the Google News homepage
    driver.get("https://news.google.com/home?hl=en-IN&gl=IN&ceid=IN:en")

    # Step 2: Waitting for the "Top stories" link to load and find it
    wait = WebDriverWait(driver, 10)
    top_stories_link = wait.until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Top stories')]"))
    )

    # Step 3: Getting the link to "Top stories"
    top_stories_url = top_stories_link.get_attribute("href")
    print(f"Navigating to Top stories: {top_stories_url}\n")

    # Step 4: Navigating to the "Top stories" page
    driver.get(top_stories_url)

    # Step 5: Waitting for the page to load
    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))

    # Step 6: Preparing CSV file
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Headline", "Link", "Image Filename"])  # Write CSV header

        # Step 7: Locating and extracting all headlines, links, and download images
        articles = driver.find_elements(By.TAG_NAME, "article")

        for article in articles:
            try:
                # Extracting headline and its link
                headline_element = article.find_element(By.XPATH, ".//a[@class='gPFEn']")
                headline = headline_element.text.strip()
                link = headline_element.get_attribute("href")

                # Extracting the image link only if it is inside a <figure> tag
            # by doing this we get rid of small logos and other unwanted images as those come under <img> 
            
                figure_element = article.find_element(By.XPATH, ".//figure[contains(@class, 'P22Vib')]")
                image_element = figure_element.find_element(By.TAG_NAME, "img")
                image_url = image_element.get_attribute("src")

                # Downloading the image and save it locally
                image_filename = os.path.join(IMAGE_DIR, f"{headline[:50].replace(' ', '_').replace('/', '_')}.jpg")
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    with open(image_filename, "wb") as img_file:
                        for chunk in response.iter_content(1024):
                            img_file.write(chunk)

                # Writing data to the CSV file
                writer.writerow([headline, link, image_filename])

                print(f"Saved: {headline}")

            except Exception as e:
                # Skipping articles missing required elements or <figure> tags
                continue

finally:
    # Step 8: Closing the browser
    driver.quit()
    print(f"Data saved to {CSV_FILE}, and images stored in {IMAGE_DIR}.")
