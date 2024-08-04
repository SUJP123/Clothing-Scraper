import sys
import os

# Add the project root directory to the module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from models.product import Product, SessionLocal

urban_outfitters_urls = ["https://www.urbanoutfitters.com/mens-shoes-on-sale",
                             "https://www.urbanoutfitters.com/sale/mens-shirts",
                             "https://www.urbanoutfitters.com/sale/mens-jackets",
                             "https://www.urbanoutfitters.com/sale/mens-shorts",
                             "https://www.urbanoutfitters.com/sale/mens-pants",
                             "https://www.urbanoutfitters.com/sale/mens-hoodies",
                             "https://www.urbanoutfitters.com/sale/womens-shoes",
                             "https://www.urbanoutfitters.com/sale/womens-pants",
                             "https://www.urbanoutfitters.com/sale/womens-shirts",
                             "https://www.urbanoutfitters.com/sale/womens-hoodies",
                             "https://www.urbanoutfitters.com/sale/womens-shorts",
                             "https://www.urbanoutfitters.com/sale/womens-jackets",
                             "https://www.urbanoutfitters.com/sale/womens-sportwear"]
clothing_types = ["Men's Shoes", "Men's Shirts", "Men's Jackets", "Men's Shorts", "Men's Pants",
                      "Men's Hoodies", "Women's Shoes", "Women's Pants", "Women's Shirts", "Women's Hoodies",
                      "Women's Shorts", "Women's Jackets", "Women's Sportwear"]

COMPANY_NAME = "urban outfitters"

def scrape_urban_outfitters(url:str, company_name:str, clothing_type:str):

    print(f"Beginning Scraping From {url}...")

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    options = ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    for header, value in HEADERS.items():
        options.add_argument(f"{header}={value}")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Wait for the page to load completely
    time.sleep(5)  # Adjust the sleep time as needed

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    products = []
    items = soup.find_all('div', class_='c-pwa-tile-grid-inner')
    print(items)
    for item in items:
        name_tag = item.find('p', class_='o-pwa-product-tile__heading')
        name = name_tag.text.strip() if name_tag else "No Name"

        price_wrapper = item.find('p', class_='c-pwa-product-price')
        # Extract sale price
        sale_price_element = item.find('span', class_='c-pwa-product-price__current')
        sale_price = sale_price_element.text.strip()[1:] if sale_price_element else "0.0"

        # Extract original price
        original_price_element = item.find('span', class_='c-pwa-product-price__original')
        original_price = original_price_element.text.strip()[1:] if original_price_element else sale_price

        deal = float(sale_price)
        retail = float(original_price)
        discount_percentage = (1 - (deal / retail)) * 100 if retail != 0 else 0
        saved = f"{discount_percentage:.2f}% off"

        description = "Empty"

        # Extract image URL
        image_tag = item.find('img', class_='o-pwa-image__img')
        image = image_tag['src'] if image_tag else "No Image"

        external_link = item.find('a', class_='c-pwa-link')['href']
        print([name, retail, deal, saved, description, image, external_link])

        product = Product(
                name=name,
                retail=retail,
                deal=deal,
                saved=saved,
                company=company_name,
                description=description,
                clothing_type=clothing_type,
                image=image,
                external_link = 'https://www.urbanoutfitters.com' + external_link
            )
        
        products.append(product)


def save_products_to_db(products):
    db = SessionLocal()
    try:
        db.add_all(products)
        db.commit()
    except Exception as e:
        db.rollback()
        print("Error saving to database:", e)
    finally:
        db.close()

if __name__ == '__main__':

    for i in range(len(urban_outfitters_urls)):
        scrape_urban_outfitters(urban_outfitters_urls[i], COMPANY_NAME, clothing_types[i])
        break
