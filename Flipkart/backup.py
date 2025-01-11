import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
from tqdm import tqdm
import random
import os
from colorama import Fore, Style, init

# Colorama ko initialize karein
init()

# Print the ASCII logo centered in the terminal
ascii_logo = r"""
+===============================================================================+
|   _____ _ _       _              _     ____                                   |
|  |  ___| (_)_ __ | | ____ _ _ __| |_  / ___|  ___ _ __ __ _ _ __   ___ _ __   |
|  | |_  | | | '_ \| |/ / _` | '__| __| \___ \ / __| '__/ _` | '_ \ / _ \ '__|  |
|  |  _| | | | |_) |   < (_| | |  | |_   ___) | (__| | | (_| | |_) |  __/ |     |
|  |_|   |_|_| .__/|_|\_\__,_|_|   \__| |____/ \___|_|  \__,_| .__/ \___|_|     |
|            |_|                  Created By Bhikan Deshmukh |_|                |
+===============================================================================+
"""

# Function to print the logo with horizontal color split
def print_horizontal_split_logo(logo):
    # Get the terminal width
    terminal_width = os.get_terminal_size().columns
    
    # Split the logo into lines and print each line with colors
    for line in logo.strip().splitlines():
        # Trim the line to fit the terminal width
        trimmed_line = line[:terminal_width]  # Ensure line does not exceed terminal width
        line_length = len(trimmed_line)
        
        # Calculate the half point for horizontal split
        half_index = line_length // 2
        
        # Split the line into two halves
        left_half = trimmed_line[:half_index]
        right_half = trimmed_line[half_index:]

        # Check if the current line is the one with "Created By Bhikan Deshmukh"
        if "Created By Bhikan Deshmukh" in trimmed_line:
            # Split the line further to color the specific text
            created_by_part = "Created By Bhikan Deshmukh"
            before_part = trimmed_line.split(created_by_part)[0]  # Part before the red text
            after_part = trimmed_line.split(created_by_part)[1]   # Part after the red text
            
            # Create the colored line
            colored_line = f"{before_part}{Fore.RED}{created_by_part}{Fore.YELLOW}{after_part}"
            print(colored_line.center(terminal_width))
        else:
            # Print left half in blue and right half in yellow, centered
            colored_line = f"{Fore.BLUE}{left_half}{Fore.YELLOW}{right_half}"
            print(colored_line.center(terminal_width))

# Call the function to print the logo
print_horizontal_split_logo(ascii_logo)  # Print the logo with horizontal split

# Setup logging for debugging
logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants for class names used to extract data
RATINGS_CLASS_1 = 'Wphh3N d4OmzS'
RATINGS_CLASS_2 = 'HO1dRb xsbJxZ'
PRODUCT_RATING_CLASS = 'ipqd2A'
ALTERNATIVE_RATING_CLASS = 'XQDdHH'
BRAND_CLASS_1 = 'mEh187'
BRAND_CLASS_2 = 'HPETK2'

# List of user agents to use for the requests
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/116.0.5845.96 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:116.0) Gecko/20100101 Firefox/116.0 Chrome/116.0.5845.88 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.96 Safari/537.36',
    'Mozilla/5.0 (X11; CrOS x86_64 14783.83.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.88 Safari/537.36'
]

def extract_ratings_reviews_product_rating(url, retries=3):
    # Randomly select a user agent for this request
    headers = {
        'User-Agent': random.choice(USER_AGENTS)  # Use a random user agent from the list
    }

    for attempt in range(retries):
        try:
            # Make the GET request to the URL
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.content, 'html.parser')  # Parse the HTML content

            # Attempt to extract ratings and reviews
            ratings, reviews = extract_ratings(soup)

            # Determine product rating
            product_rating = extract_product_rating(soup)

            # Extract brand name
            brand = extract_brand(soup)

            # Log the extracted data
            logging.info(f"Extracted Data for {url}: Ratings={ratings}, Reviews={reviews}, Product Rating={product_rating}, Brand={brand}")

            return ratings, reviews, product_rating, brand

        except (requests.RequestException, ValueError) as e:
            logging.error(f"Error fetching data from {url} on attempt {attempt + 1}: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff for retries

    return "0", "0", "0", None  # Return default values if all attempts fail

def extract_ratings(soup):
    # Extract ratings and reviews from the specified HTML structure
    ratings_reviews = soup.find('span', class_=RATINGS_CLASS_1)
    if ratings_reviews:
        try:
            ratings, reviews = map(str.strip, ratings_reviews.get_text(strip=True).split('and'))  # Split ratings and reviews
            ratings = ratings.replace('ratings', '').replace(',', '')  # Clean up the ratings text
            return ratings, reviews.replace('reviews', '')  # Clean up the reviews text
        except ValueError:
            logging.warning(f"Error parsing ratings and reviews from {ratings_reviews}")

    ratings_section = soup.find('div', class_=RATINGS_CLASS_2)
    if ratings_section:
        ratings_text = ratings_section.find('span', string=lambda t: 'Ratings' in t)  # Find ratings text
        reviews_text = ratings_section.find('span', string=lambda t: 'Reviews' in t)  # Find reviews text
        ratings = ratings_text.get_text(strip=True).split(' ')[0].replace(',', '') if ratings_text else "0"  # Get rating count
        reviews = reviews_text.get_text(strip=True).split(' ')[0] if reviews_text else "0"  # Get review count
        return ratings, reviews

    return "0", "0"  # Return default if no ratings found

def extract_product_rating(soup):
    # Extract product rating from the HTML
    product_rating_div = soup.find('div', class_=PRODUCT_RATING_CLASS)
    if product_rating_div:
        return product_rating_div.get_text(strip=True) or "0"  # Return the product rating if found

    # Check for alternative ratings
    alternative_rating_divs = soup.find_all('div', class_=ALTERNATIVE_RATING_CLASS)
    for alt_div in alternative_rating_divs:
        if alt_div.get_text(strip=True):
            return alt_div.get_text(strip=True)  # Return first valid alternative rating

    return "0"  # Return default if no rating found

def extract_brand(soup):
    # Extract the brand name from the HTML
    brand_element = soup.find('span', class_=BRAND_CLASS_1)
    if brand_element:
        return brand_element.get_text(strip=True).replace('Brand Name', '').strip()  # Clean and return brand name
    
    brand_element = soup.find('li', class_=BRAND_CLASS_2)
    return brand_element.get_text(strip=True) if brand_element else None  # Return brand if found

def scrape_and_save_to_csv(input_csv, output_csv):
    # Read URLs from input CSV and save results to output CSV
    try:
        with open(input_csv, mode='r', newline='', encoding='utf-8') as infile, \
             open(output_csv, mode='a', newline='', encoding='utf-8') as outfile:
            
            reader = csv.reader(infile)  # Read CSV file
            writer = csv.writer(outfile)  # Prepare to write to CSV
            urls = list(reader)  # Convert reader to a list

            # Write header only if the output file is empty
            if outfile.tell() == 0:
                writer.writerow(['URL', 'Ratings', 'Reviews', 'Product Rating', 'Brand'])

            # Loop through each URL and scrape data
            for row in tqdm(urls, desc="Scraping Progress", unit="url"):
                url = row[0]
                if url:
                    # Extract data for the URL and write it to the output CSV
                    ratings, reviews, product_rating, brand = extract_ratings_reviews_product_rating(url)
                    writer.writerow([url, ratings, reviews, product_rating, brand or ""])

    except Exception as e:
        logging.error(f"Error processing the CSV files: {e}")
        print(f"Error processing the CSV files: {e}")

# Define the input CSV and output CSV files
input_csv_file = 'urls.csv'  # Input file containing URLs to scrape
output_csv_file = 'Ratings Reviews.csv'  # Output file for scraped data

# Call the function to start scraping and saving data
scrape_and_save_to_csv(input_csv_file, output_csv_file)

print("Script completed. Check 'Ratings Reviews.csv' for results and 'scraper.log' for logs.")
