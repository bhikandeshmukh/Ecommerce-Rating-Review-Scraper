
# Bulk Product Ratings and Reviews Scraping

This project is a Python-based web scraping tool designed to extract bulk product ratings, reviews, and related details from popular e-commerce websites such as Amazon, Myntra, and Flipkart.

## Features

- **Amazon**:
  - Scrapes star ratings and rating counts.

- **Myntra**:
  - Scrapes star ratings and rating counts.

- **Flipkart**:
  - Scrapes star ratings, rating counts, available sizes (XS, S, M, L, XL, XXL), brand, and price.

## Example Output

| URL | Ratings | Reviews | Product Rating | Brand | Price | XS | S | M | L | XL | XXL |
| --- | ------- | ------- | --------------- | ----- | ----- | -- | - | - | - | -- | --- |
| https://www.flipkart.com/product/p/itme?pid=TOPH3H3U4JDTGZVM | 12753 | 1,304 | 3.8 | Serein | 399 | Yes | Yes | Yes | Yes | Yes | Yes |

## Requirements

- Python 3.x
- Required Python libraries:
  - `requests`
  - `beautifulsoup4`
  - `pandas`

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/bhikandeshmukh/Ecommerce-Rating-Review-Scraper.git
   cd Ecommerce-Rating-Review-Scraper
   ```

2. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the scraper script:
   ```bash
   python scraper.py
   ```

## Notes

- Ensure that the target website's terms of service are respected while scraping data.
- Use appropriate headers and delays to avoid being flagged as a bot.

## Output

The scraper outputs the collected data into a CSV file in the following format:
```
URL, Ratings, Reviews, Product Rating, Brand, Price, XS, S, M, L, XL, XXL
https://www.flipkart.com/product/p/itme?pid=TOPH3H3U4JDTGZVM, 12753, 1,304, 3.8, Serein, 399, Yes, Yes, Yes, Yes, Yes, Yes
```

## License

This project is licensed under the MIT License.
