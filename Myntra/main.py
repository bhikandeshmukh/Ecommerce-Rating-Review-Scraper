import os
import requests
import re
import csv
from tqdm import tqdm  # Import tqdm for the progress bar

# Input file containing the URLs
input_file = 'urls.txt'
# Output folder to save HTML files
output_folder = 'html'
# CSV output file
csv_output_file = 'output.csv'

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Function to download HTML content
def download_html(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None

# Function to extract required data from HTML
def extract_data(html_content):
    # Search for averageRating and totalCount anywhere in the HTML content
    avg_pattern = r'"averageRating":([\d.]+)'
    count_pattern = r'"totalCount":(\d+)'

    # Find all occurrences
    average_rating_matches = re.findall(avg_pattern, html_content)
    total_count_matches = re.findall(count_pattern, html_content)

    # If there are matches, return the last found; if not found, return '0'
    average_rating = average_rating_matches[-1] if average_rating_matches else '0'
    total_count = total_count_matches[-1] if total_count_matches else '0'

    return average_rating, total_count

# Read URLs from the input file
with open(input_file, 'r') as file:
    urls = [line.strip() for line in file if line.strip()]

data_rows = []

# Use tqdm to create a progress bar for downloading
with tqdm(total=len(urls), desc="Downloading HTML files", unit="file") as pbar:
    for url in urls:
        numeric_id = ''.join(filter(str.isdigit, url))

        if not numeric_id:
            print(f"No numeric ID found in URL: {url}. Skipping.")
            pbar.update(1)
            continue

        # Check if the HTML file already exists
        output_file = os.path.join(output_folder, f"{numeric_id}.html")

        if os.path.exists(output_file):
            print(f"File already exists: {output_file}. Skipping download.")
            with open(output_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
        else:
            # Download HTML content if it doesn't exist
            html_content = download_html(url)
            if html_content is not None:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            else:
                print(f"Failed to download {url}. Skipping.")
                pbar.update(1)
                continue

        # Extract averageRating and totalCount
        average_rating, total_count = extract_data(html_content)
        data_rows.append([output_file, average_rating, total_count])

        pbar.update(1)

# Handle the CSV output file safely
try:
    with open(csv_output_file, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['File Name', 'Average Rating', 'Total Count'])
        csv_writer.writerows(data_rows)

    print(f"Data extracted and saved to {csv_output_file}")

except PermissionError:
    print(f"Permission denied: Unable to write to {csv_output_file}. Please check if it is open or has the correct permissions.")