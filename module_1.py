from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Setting up Chrome driver
driver = webdriver.Chrome()

try:
    # Opening Google News
    driver.get("https://news.google.com/home?hl=en-IN&gl=IN&ceid=IN:en")

    # Waitting for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
    )

    # Finding all <a> tags on the page
    all_links = driver.find_elements(By.TAG_NAME, "a")
    print(f"Found {len(all_links)} links on the page.\n")  # Debugging

    # Extracting and printing only those <a> tags that have meaningful text (headline) and a valid href (link)
    for link in all_links:
        try:
            headline = link.text.strip()  # Extracting text inside <a>
            news_link = link.get_attribute("href")  # Extracting the URL
            
            # Printing only if both headline and link exist
            if headline and news_link and "http" in news_link:
                print(f"Headline: {headline}")
                print(f"News Link: {news_link}\n")

        except NoSuchElementException:
            continue  # Skiping elements that don't have a headline or URL

except TimeoutException:
    print("Timeout: Could not load Google News homepage.")

finally:
    # Closing the browser
    driver.quit()
