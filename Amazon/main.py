import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# 10 Desktop User-Agent Strings
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/92.0.902.73 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/78.0.4093.147",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
]

# Browser profiles (Accept-Language and Referer headers)
browser_profiles = [
    {'Accept-Language': 'en-US,en;q=0.9', 'Referer': 'https://www.amazon.com/'},
    {'Accept-Language': 'en-GB,en;q=0.9', 'Referer': 'https://www.amazon.in/'},
    {'Accept-Language': 'en-CA,en;q=0.9', 'Referer': 'https://www.amazon.ca/'},
    {'Accept-Language': 'de-DE,de;q=0.9', 'Referer': 'https://www.amazon.de/'},
    {'Accept-Language': 'fr-FR,fr;q=0.9', 'Referer': 'https://www.amazon.fr/'}
]

# CSV file reading function to get URLs
def read_urls_from_csv(file_path):
    df = pd.read_csv(file_path)
    return df['url'].tolist()

# Function to get the page content with retry logic
def get_page_content(url, retries=3):
    headers = {
        'User-Agent': random.choice(user_agents),  # Random user-agent
        'Accept-Language': random.choice(browser_profiles)['Accept-Language'],  # Random Accept-Language
        'Referer': random.choice(browser_profiles)['Referer']  # Random Referer
    }
    
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Check if the request was successful
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url} (Attempt {attempt + 1}/{retries}): {e}")
            attempt += 1
            time.sleep(random.uniform(2, 5))  # Sleep before retrying
    
    # If all attempts fail, return None
    return None

# Function to scrape ratings and review count
def scrape_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # First attempt: Try to scrape using the first HTML structure
    rating = soup.find('span', {'data-hook': 'rating-out-of-text'})
    review_count = soup.find('span', {'data-hook': 'total-review-count'})
    
    if rating and review_count:
        return rating.text.strip(), review_count.text.strip()
    
    # Fallback: Try to scrape using the second HTML structure
    rating = soup.find('span', {'class': 'a-size-base a-color-base'})
    review_count = soup.find('span', {'id': 'acrCustomerReviewText'})
    
    if rating and review_count:
        return rating.text.strip(), review_count.text.strip()
    
    return None, None

# Log file function
def log_failed_scrape(url, reason):
    with open("scraping_log.txt", "a") as log_file:
        log_file.write(f"Failed to scrape {url}: {reason}\n")

# Function to process URLs and save results to CSV (using ThreadPoolExecutor for faster processing)
def process_urls(file_path, output_csv):
    urls = read_urls_from_csv(file_path)
    results = []
    
    def scrape_url(url):
        html = get_page_content(url)
        if html:
            rating, review_count = scrape_data(html)
            if rating and review_count:
                return {'URL': url, 'Rating': rating, 'Review Count': review_count}
            else:
                # If no rating/review found, set both to "0"
                results.append({'URL': url, 'Rating': '0', 'Review Count': '0'})
                log_failed_scrape(url, "Missing rating or review count")
        else:
            # Log failure to get page content
            log_failed_scrape(url, "Failed to fetch content")
            return {'URL': url, 'Rating': '0', 'Review Count': '0'}
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        for result in tqdm(executor.map(scrape_url, urls), total=len(urls), desc="Scraping URLs", ncols=100, unit="url"):
            if result:
                results.append(result)
    
    # Save the results to a CSV file
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"Data saved to {output_csv}")

# Example usage
csv_file_path = 'urls.csv'  # CSV file containing the URLs
output_csv_path = 'scraped_data.csv'  # Output CSV file for the scraped data
process_urls(csv_file_path, output_csv_path)
