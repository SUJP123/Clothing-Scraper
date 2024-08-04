import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

adidas_urls = ["https://www.adidas.com/us/men-shoes-sale",
               "https://www.adidas.com/us/men-pants-sale",
               "https://www.adidas.com/us/men-hoodies_sweatshirts-sale",
               "https://www.adidas.com/us/men-t_shirts-sale",
               "https://www.adidas.com/us/men-jackets-sale",
               "https://www.adidas.com/us/men-track_suits-sale",
               "https://www.adidas.com/us/women-shoes-sale",
               "https://www.adidas.com/us/women-pants-sale",
               "https://www.adidas.com/us/women-hoodies_sweatshirts-sale",
               "https://www.adidas.com/us/women-t_shirts-sale",
               "https://www.adidas.com/us/women-skirts_dresses-sale",
               "https://www.adidas.com/us/women-jackets-sale"]


import time
from bs4 import BeautifulSoup
import requests
from models.product import Product, SessionLocal, reset_table
import httpx
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
#from models.product import Product, SessionLocal, reset_table


COMPANY_NAME = 'adidas'

def scrape_adidas(url: str, company_name: str):
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

    driver = webdriver.Chrome()

    driver.get(url)

    while len(driver.find_elements(By.CLASS_NAME, 'product-card-content-badges-wrapper___2RWqS')) < 1:
        time.sleep(1)
    time.sleep(3)

    prices_elements = driver.find_elements(By.CLASS_NAME, 'product-card-content-badges-wrapper___2RWqS')
    prices = []
    for price_element in prices_elements:
        try:
            prices.append(price_element.text.replace('\n', '').strip())
        except:
            print("StaleElementReferenceException caught. Re-locating the element.")
            prices_elements = driver.find_elements(By.CLASS_NAME, 'product-card-content-badges-wrapper___2RWqS')
            prices.append(price_element.text.replace('\n', '').strip())

    driver.quit()

    req = httpx.get(url, headers=HEADERS)
    soup = BeautifulSoup(req.content, "html.parser")

    products = []

    for item, price in zip(soup.find_all('div', class_='grid-item'), prices):
        name = item.find('p', 'glass-product-card__title').text if item.find('p', 'glass-product-card__title') else None
        descriptions = item.find('span', class_='dark-grey___6ysQv').text if item.find('span', 'dark-grey___6ysQv') else None
        clothing_types = item.find('p', 'glass-product-card__category').text if item.find('p', 'glass-product-card__category') else None
        images = item.find('img', 'glass-product-card__primary-image')['src'] if item.find('img', 'glass-product-card__primary-image') else None
        external_links = item.find('a', 'glass-product-card__assets-link')['href'] if item.find('a', 'glass-product-card__assets-link') else None
        
        discount, retail_price, deal_price = None, None, None
        if price:
            price_parts = price.split('$')
            if len(price_parts) == 3:
                discount = price_parts[0][1:] + " off"
                retail_price = float(f"{price_parts[1]}")
                deal_price = float(f"{price_parts[2]}")
        else:
            continue
        
        product_info = Product(
            name=name,
            retail=retail_price,
            deal=deal_price,
            saved=discount,
            company=company_name,
            description=descriptions,
            clothing_type=clothing_types,
            image=images,
            external_link = 'https://www.adidas.com' + external_links
        )
        products.append(product_info)

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
    for adidas_url in adidas_urls:
        scrape_adidas(adidas_url, COMPANY_NAME)