# Google News Scraper

## Overview
This project is a web scraper that extracts headlines, article URLs, and images from Google News. The extracted data is stored in a MongoDB database with a structured schema for better organization and retrieval. The project is designed for automation and can be scheduled to run periodically using a cron job.

## Features
- Scrapes the Google News homepage dynamically.
- Extracts "Top Stories" section without hardcoding the section name.
- Handles lazy loading of news articles.
- Stores extracted data into a MongoDB database.
- Implements a de-duplication strategy using a unique hash of the headline and URL.
- Logs execution timestamps, errors, and processing details.
- Can be scheduled as a cron job for automated execution.

## Modules

### 1. `module_1.py`: Scrape Google News Homepage
- Extracts all article links from Google News homepage.
- Avoids hardcoded URLs and section names.
- Outputs headline and link for each story.

### 2. `module_2_3.py`: Extract Headlines & Thumbnails
- Navigates to the "Top Stories" section dynamically.
- Extracts headlines, URLs, and thumbnails.
- Handles lazy loading for complete data extraction.

### 3. `module_4_5.py`: Store Data in MongoDB
- Saves extracted data in MongoDB database `google_news_database`.
- Uses separate collections:
  - `news_articles`: Stores headlines, article URLs, timestamps, and image references.
  - `news_images`: Stores image binary data along with image URLs.
- Implements de-duplication using SHA-256 hashing of headlines and URLs.

### 4. `module_6.py`: Orchestration & Logging
- Manages execution of all modules in sequence.
- Logs execution details, errors, and status messages.
- Designed for cron job scheduling.

## Database Schema
The data is stored in a MongoDB database named `google_news_database` with two collections:

### Collection: `news_articles`
| Field              | Type          | Description |
|-------------------|--------------|-------------|
| `_id`            | ObjectId      | Unique identifier |
| `headline`       | String        | News article title |
| `link`           | String        | URL to the article |
| `scrape_timestamp` | DateTime      | Time when data was scraped |
| `image_id`       | ObjectId (Ref) | Reference to `news_images` collection |
| `hash`           | String (SHA-256) | Unique hash for deduplication |

### Collection: `news_images`
| Field        | Type    | Description |
|-------------|--------|-------------|
| `_id`      | ObjectId | Unique identifier |
| `image`    | Binary  | Image binary data |
| `image_url` | String  | Original image URL |

## Installation & Setup

### Prerequisites
- Python 3.x
- MongoDB
- Chrome WebDriver
- Required Python packages:
  - os
  -	requests
  -	pymongo
  -	hashlib
  -	logging
  -	datetime 
  -	selenium   
  -	selenium.webdriver.common.by
  -	selenium.webdriver.support.ui 
  -	selenium.webdriver.chrome.options 


```bash
pip install selenium pymongo requests
```

### Configuration
Ensure MongoDB is running locally on `mongodb://localhost:27017/`. Modify the database connection string in `module_4_5.py` and `module_6.py` if necessary.

### Running the Scraper

To execute the entire pipeline:

```bash
python module_6.py
```

## Scheduling with Cron Job

To automate the scraper, schedule it as a cron job:

1. Open the cron job editor:

```bash
crontab -e
```

2. Add the following line to run the script every day at 8 AM:

```bash
0 8 * * * /usr/bin/python3 /path/to/module_6.py >> /path/to/news_scraper.log 2>&1
```

- Replace `/path/to/module_6.py` with the actual path to your script.
- Logs are saved in `news_scraper.log`.

## Logging
The scraper logs execution details in `news_scraper.log` with:
- Start and end timestamps
- Extracted data details
- Errors and debugging messages

## Future Enhancements
- Support for additional news categories.
- More advanced duplicate detection using NLP.
- Parallel scraping for faster execution.
- API for querying stored news articles.

## License
This project is licensed under the MIT License.

