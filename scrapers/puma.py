import sys
import os

#UPDATE Scrolling Method


puma_urls = ["https://us.puma.com/us/en/sale/all-sale?pref_gender=Men&pref_productdivName=Shoes&offset=24",
             "https://us.puma.com/us/en/sale/all-sale?pref_gender=Men&pref_productdivName=Clothing&pref_style=Shirts",
             "https://us.puma.com/us/en/sale/all-sale?pref_gender=Men&pref_productdivName=Clothing&pref_style=Jackets",
             "https://us.puma.com/us/en/sale/all-sale?pref_gender=Men&pref_productdivName=Clothing&pref_style=Shorts",
             "https://us.puma.com/us/en/sale/all-sale?pref_gender=Men&pref_productdivName=Clothing&pref_style=Pants",
             "https://us.puma.com/us/en/sale/all-sale?pref_gender=Men&pref_productdivName=Clothing&pref_style=Hoodies+and+Sweatshirts",
             "https://us.puma.com/us/en/sale/all-sale?pref_gender=Women&pref_productdivName=Shoes",
             "https://us.puma.com/us/en/sale/all-sale?pref_gender=Women&pref_productdivName=Clothing&pref_style=Leggings%2CPants",
             "https://us.puma.com/us/en/sale/all-sale?pref_gender=Women&pref_productdivName=Clothing&pref_style=Shirts%2CTees",
             "https://us.puma.com/us/en/sale/all-sale?pref_gender=Women&pref_productdivName=Clothing&pref_style=Hoodies+and+Sweatshirts",
             "https://us.puma.com/us/en/sale/all-sale?pref_gender=Women&pref_productdivName=Clothing&pref_style=Shorts%2CSkirts",
             "https://us.puma.com/us/en/sale/all-sale?pref_gender=Women&pref_productdivName=Clothing&pref_style=Jackets",
             "https://us.puma.com/us/en/sale/all-sale?pref_gender=Women&pref_productdivName=Clothing&pref_style=Sports+Bras%2CTank+Tops"]
clothing_types = ["Men's Shoes", "Men's Shirts", "Men's Jackets", "Men's Shorts", "Men's Pants",
                   "Men's Hoodies", "Women's Shoes", "Women's Pants" , "Women's Shirts", "Women's Hoodies", 
                   "Women's Shorts", "Women's Jackets", "Women's Sportwear"]

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


COMPANY_NAME = "puma"

def scrape_puma(url:str, company_name:str, clothing_type:str):

    print(f"Beginning Scraping From {url}...")

    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')

    products = [ ]
    items = soup.find_all('li', {'data-test-id': 'product-list-item'})
    for item in items:
        name_tag = item.find('h3', class_='w-full')
        name = ''.join(name_tag.find(string=True, recursive=False)).strip()

        # Extract sale price
        sale_price_element = item.find('span', {'data-test-id': 'sale-price'}).text
        deal = float(sale_price_element[1:])

        # Extract retail price
        price_element = item.find('span', {'data-test-id': 'price'}).text
        retail = float(price_element[1:])

        discount_percentage = (1 - (deal / retail)) * 100
        saved = f"{discount_percentage:.2f}% off"

        description = "Empty"

        image = item.find('img', class_='w-full')['src']

        external_link = item.find('a', class_='tw-hqslau tw-xbcb1y')['href']

        product = Product(
                name=name,
                retail=retail,
                deal=deal,
                saved=saved,
                company=company_name,
                description=description,
                clothing_type=clothing_type,
                image=image,
                external_link = 'https://us.puma.com' + external_link
            )
        
        products.append(product)
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
    for i in range(len(puma_urls)):
        scrape_puma(puma_urls[i], COMPANY_NAME, clothing_types[i])