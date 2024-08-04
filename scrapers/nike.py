# scrapers/nike.py
import sys
import os


nike_urls = ["https://www.nike.com/w/sale-shoes-3yaepzy7ok",
             "https://www.nike.com/w/sale-jordan-shoes-37eefz3yaepzy7ok",
             "https://www.nike.com/w/sale-hoodies-pullovers-3yaepz6rive",
             "https://www.nike.com/w/sale-pants-tights-2kq19z3yaep",
             "https://www.nike.com/w/sale-jackets-vests-3yaepz50r7y",
             "https://www.nike.com/w/sale-tops-t-shirts-3yaepz9om13",
             "https://www.nike.com/w/sale-shorts-38fphz3yaep",
             "https://www.nike.com/w/sale-sports-bras-3yaepz40qgm",
             "https://www.nike.com/w/sale-surf-swimwear-3yaepzq3un",
             "https://www.nike.com/w/sale-skirts-dresses-3yaepz8y3qp",
             "https://www.nike.com/w/sale-jumpsuits-rompers-3yaepz4w2rm",
             "https://www.nike.com/w/sale-tracksuits-3iha1z3yaep",
             "https://www.nike.com/w/sale-compression-baselayer-3yaepz4pwb",
             "https://www.nike.com/w/sale-socks-3yaepzuwr3"]

# Add the project root directory to the module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import requests
import time
from bs4 import BeautifulSoup
from models.product import Product, SessionLocal, reset_table
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


COMPANY_NAME = "nike"


def scrape_nike(url : str, company_name: str):

    print(f"Beginning Scraping From {url}...")

    browser_options = ChromeOptions()
    browser_options.add_argument('--headless')
    browser_options.add_argument('--disable-gpu')
    browser_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=browser_options)
    driver.get(url)
    time.sleep(5)

    print("Starting Nike Scroll")
    #Load full page
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(100)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    try:
        WebDriverWait(driver, 1000).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-card__hero-image'))
        )
    except Exception as e:
        print("Error waiting for images to load:", e)

    page_source = driver.page_source
    driver.quit()

    print("Finished Nike Scroll")

    response = requests.get(url)
    soup = BeautifulSoup(page_source, "html.parser")

    products = [ ]

    for item in soup.find_all('div', class_='product-card'):
        print("Item scrape")
        try:
            name = item.find('div', class_='product-card__title').text

            price_wrapper = item.find('div', class_='product-price__wrapper')
            current_price = price_wrapper.find('div', {'aria-hidden': 'true', 'data-testid': 'product-price-reduced'}).text.replace('$', '').replace(',', '')
            original_price = price_wrapper.find('div', {'aria-hidden': 'true', 'data-testid': 'product-price'}).text.replace('$', '').replace(',', '')

            retail_price = float(original_price)
            deal_price = float(current_price)

            discount_percentage = (1 - (deal_price / retail_price)) * 100
            saved = f"{discount_percentage:.2f}% off"

            description = item.find('div', class_='product-card__product-count').text

            clothing_type = item.find('div', class_='product-card__subtitle').text

            image = item.find('img', class_='product-card__hero-image')['src']
            
            external_link = item.find('a', class_='product-card__link-overlay')['href']
            

            
            product = Product(
                name=name,
                retail=retail_price,
                deal=deal_price,
                saved=saved,
                company=company_name,
                description=description,
                clothing_type=clothing_type,
                image=image,
                external_link = external_link
            )

            products.append(product)
        except Exception as e:
            print("Error extracting product:", e)
        
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
    reset_table()
    for nike_url in nike_urls:
        scrape_nike(nike_url, COMPANY_NAME)