import sys
import os

# Add the project root directory to the module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import requests
from bs4 import BeautifulSoup
from models.product import Product, SessionLocal, reset_table
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
import time

# Forever 21 URLs for scraping
forever21_urls = [
    "https://www.forever21.com/us/shop/catalog/category/21men/mens-sale-graphic-tops",
    "https://www.forever21.com/us/shop/catalog/category/21men/mens-sale-tops",
    "https://www.forever21.com/us/shop/catalog/category/21men/mens-sale-bottoms",
    "https://www.forever21.com/us/shop/catalog/category/21men/mens-sale-sweaters",
    "https://www.forever21.com/us/shop/catalog/category/21men/mens-sale-jackets",
    "https://www.forever21.com/us/shop/catalog/category/f21/sale_tops",
    "https://www.forever21.com/us/shop/catalog/category/f21/sale_dresses",
    "https://www.forever21.com/us/shop/catalog/category/f21/sale_bottoms",
    "https://www.forever21.com/us/shop/catalog/category/f21/sale_outerwear",
    "https://www.forever21.com/us/shop/catalog/category/f21/sale_sweaters",
    "https://www.forever21.com/us/shop/catalog/category/f21/sale_activewear"
    ]

clothing_types = ["Men's Shirts", "Men's Shirts", "Men's Pants", "Men's Sweaters", 
                  "Men's Jackets", "Women's Shirts", "Women's Dresses", "Women's Pants", 
                  "Women's Jackets", "Women's Sweaters", "Women's Sportswear"]

COMPANY_NAME = "forever 21"

def scrape_forever21(url: str, company_name: str, clothing_type: str):
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
    items = soup.find_all('div', class_='product-tile product-tile--default')

    for item in items:
        try:
            name_tag = item.find('a', class_='product-tile__name')
            name = name_tag.find('p').text.replace('\n', '')

            # Extract sale price
            sale_price_element = item.find_all('span', class_='value')
            deal = round(float(sale_price_element[1].text.replace('$', '')), 2)
            retail = round(float(sale_price_element[0].text.replace('$', '')), 2)

            discount_percentage = round((1 - (deal / retail)) * 100, 2)
            saved = str(discount_percentage) + "%% off"[1:] if discount_percentage else None

            description = "Empty"

            # Extract image URL
            img_element = item.find('img', class_='product-tile__image')
            image = img_element['src'] if img_element else None

            # Extract product link
            link_element = item.find('a', class_='product-tile__anchor')
            external_link = link_element['href'] if link_element else None
            print([name, retail, deal, saved, company_name, description, clothing_type, image, external_link])

            product = Product(
                name=name,
                retail=retail,
                deal=deal,
                saved=saved,
                company=company_name,
                description=description,
                clothing_type=clothing_type,
                image=image,
                external_link='https://www.forever21.com' + external_link if external_link else None
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
    for i in range(len(forever21_urls)):
        scrape_forever21(forever21_urls[i], COMPANY_NAME, clothing_types[i])
