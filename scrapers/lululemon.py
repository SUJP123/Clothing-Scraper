import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import requests
from bs4 import BeautifulSoup
from models.product import Product, SessionLocal, reset_table
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
import time

# Lululemon URLs for scraping
lululemon_urls = [
    "https://shop.lululemon.com/c/sale/_/N-1z0xcmkZ1z0xbazZ1z0xbbfZ8t6",
    "https://shop.lululemon.com/c/sale/_/N-1z0xbcmZ1z0xbckZ1z0xbakZ8t6Z1z0xcmk",
    "https://shop.lululemon.com/c/sale/_/N-1z0xbb9Z8t6Z1z0xcmk",
    "https://shop.lululemon.com/c/sale/_/N-1z0xbanZ8t6Z1z0xcmk",
    "https://shop.lululemon.com/c/sale/_/N-1z0xcuuZ1z0xbb9Z8t6",
    "https://shop.lululemon.com/c/sale/_/N-1z0xbanZ8t6Z1z0xcuu",
    "https://shop.lululemon.com/c/sale/_/N-1z0xbbeZ1z0xbbfZ1z0xbcfZ8t6Z1z0xcuu",
    "https://shop.lululemon.com/c/sale/_/N-1z0xbckZ8t6Z1z0xcuu",
    "https://shop.lululemon.com/c/sale/_/N-1z0xbadZ8t6Z1z0xcuu"]

clothing_types = ["Men's Pants", "Men's Shirts", "Men's Shorts", 
                  "Men's Hoodies", "Women's Shorts", "Women's Hoodies", 
                  "Women's Pants", "Women's Shirts", "Women's Sweaters"]

image_ids = ['us_151555975_0','us_121275039_0', 'us_146053259_0', 
             'us_151625491_0', 'us_125000107_0', 'us_149508332_0', 
             'us_104700069_0', 'us_148225489_0', 'us_145304416_0']

COMPANY_NAME = "lululemon"

def scrape_lululemon(url: str, company_name: str, clothing_type: str, imageId:str):
    print(f"Beginning Scraping From {url}...")

    # Set up Selenium WebDriver
    options = ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    
    # Open the URL
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    # Get page source and close the driver
    page_source = driver.page_source
    driver.quit()

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    products = []
    items = soup.find_all('div', class_='product-tile')
    for item in items:
        try:
            # Extract name
            name_tag = item.find('h3', class_='product-tile__product-name')
            name = name_tag.get_text(strip=True) if name_tag else None

            # Extract sale price
            sale_price_element = item.find('span', class_='price-1jnQj').find_all('span')
            deal = float(sale_price_element[1].text[1:])

            # Extract retail price
            price_element = item.find('span', class_='priceInactiveListPrice-l7Nnb price__inactive-list-price').find_all('span')
            retail = float(price_element[1].text[1:])

            discount_percentage = round((1 - (deal / retail)) * 100, 2) if deal and retail else None
            saved = str(discount_percentage) + '%% off'[1:] if discount_percentage else None
            description = "Empty"

            img_element = soup.find('img', id=imageId)
            srcset = img_element['srcset']
            srcset_urls = [url.strip().split(' ') for url in srcset.split(',') if url.strip()]
            # Select the highest resolution image URL
            image = srcset_urls[-6][0]

            # Extract product link
            link_element = item.find('a', class_='link')
            external_link = link_element['href'] if link_element else None
    
            product = Product(
                name=name,
                retail=retail,
                deal=deal,
                saved=saved,
                company=company_name,
                description=description,
                clothing_type=clothing_type,
                image=image,
                external_link='https://shop.lululemon.com' + external_link
            )

            products.append(product)

        except Exception as e:
            print(f"Error processing item: {e}")
    save_products_to_db(products)


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
    for i in range(0, len(lululemon_urls)):
        scrape_lululemon(lululemon_urls[i], COMPANY_NAME, clothing_types[i], image_ids[i])
