import sys
import os

# Add the project root directory to the module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import time
from bs4 import BeautifulSoup
from models.product import Product, SessionLocal, reset_table
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

COMPANY_NAME = 'shein'
shein_urls = [
    "https://us.shein.com/RecommendSelection/All-Sale-sc-017210185.html?categoryJump=true&ici=us_tab02navbar02&src_identifier=fc%3DSale%60sc%3DSale%60tc%3D0%60oc%3D0%60ps%3Dtab02navbar02%60jc%3DitemPicking_017210185&src_module=topcat&src_tab_page_id=page_home1722492211371&child_cat_id=1970&source=insideFilter&sourceStatus=1&page=1"
]

def scrape_shein(url, company_name):
    browser_options = ChromeOptions()
    browser_options.add_argument('--headless')
    browser_options.add_argument('--disable-gpu')
    browser_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=browser_options)
    driver.get(url)
    time.sleep(15)
    
    page_source = driver.page_source
    driver.quit()

    soup = BeautifulSoup(page_source, "html.parser")
    print(soup)
    
    products = []

    for item in soup.find_all('section', class_='product-card'):
        try:
            name_element = item.find('a', class_='goods-title-link')
            if not name_element:
                continue
            name = name_element['data-title']

            current_price_element = item.find('p', class_='product-item__camecase-wrap')
            if not current_price_element:
                continue
            current_price = current_price_element.text.replace('$', '').replace(',', '')
            deal_price = float(current_price)

            discount_percentage_element = item.find('div', class_='product-card__discount-label')
            if not discount_percentage_element:
                continue
            discount_percentage = discount_percentage_element.text.strip('%-')
            discount_percentage = float(discount_percentage)
            original_price = deal_price / (1 - (discount_percentage / 100))
            retail_price = float(original_price)
            saved = f"{discount_percentage:.0f}% off"

            description_element = item.find('p', class_='product-card__selling-proposition-text')
            description = description_element.text if description_element else ''

            clothing_type = "Men's Shirt"

            image_element = item.find('img', class_='fsp-element')
            image = image_element['src'] if image_element else ''

            external_link_element = item.find('a', class_='S-product-card__img-container')
            external_link = external_link_element['href'] if external_link_element else ''

            product = Product(
                name=name,
                retail=retail_price,
                deal=deal_price,
                saved=saved,
                company=company_name,
                description=description,
                clothing_type=clothing_type,
                image=image,
                external_link=external_link
            )
            print(product)
            products.append(product)
        except Exception as e:
            print("Error extracting product:", e)


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
    for shein_url in shein_urls:
        scrape_shein(shein_url, COMPANY_NAME)
