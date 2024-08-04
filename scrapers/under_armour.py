import sys
import os


under_armour_urls = ["https://www.underarmour.com/en-us/c/outlet/mens/shoes/",
                     "https://www.underarmour.com/en-us/c/outlet/mens/tops/",
                     "https://www.underarmour.com/en-us/c/outlet/mens/bottoms/",
                     "https://www.underarmour.com/en-us/c/outlet/mens/outerwear/",
                     "https://www.underarmour.com/en-us/c/outlet/mens/shorts/",
                     "https://www.underarmour.com/en-us/c/outlet/womens/shoes/",
                     "https://www.underarmour.com/en-us/c/outlet/womens/tops/",
                     "https://www.underarmour.com/en-us/c/outlet/womens/bottoms/",
                     "https://www.underarmour.com/en-us/c/outlet/womens/outerwear/",
                     "https://www.underarmour.com/en-us/c/outlet/womens/sports-bras/",
                     "https://www.underarmour.com/en-us/c/outlet/womens/shorts/"]
clothing_styles = ["Men's Shoes", "Men's Shirts", "Men's Pants", "Men's Jackets"
                   , "Men's Shorts", "Women's Shoes", "Women's Shirts", "Women's Pants",
                     "Women's Jackets", "Women's Sports Bras", "Women's Shorts"]

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


COMPANY_NAME = "under armour"

def scrape_under_armour(url:str, company_name:str, clothing_type:str):

    print(f"Scraping from {url}")

    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    items = soup.find_all('div', class_='false')
    products = [ ]

    for item in items:
        name = item.find('a', class_='ProductTile_product-item-link__tSc19').text

        prices = item.find('div', class_='PriceDisplay_sr-price__NA35y').text
        price_list = prices.split(' ')
        retail = float(price_list[2][1:][:-1])
        deal = float(price_list[-1][1:][:-1])
        discount_percentage = (1 - (deal / retail)) * 100
        saved = f"{discount_percentage:.2f}% off"

        description = "Empty"

        image = item.find('img', class_='Image_responsive_image__Hsr2N')['src']
        external_link = item.find('a', class_='ProductTile_product-item-link__tSc19')['href']

        product = Product(
                name=name,
                retail=retail,
                deal=deal,
                saved=saved,
                company=company_name,
                description=description,
                clothing_type=clothing_type,
                image=image,
                external_link = 'https://www.underarmour.com' + external_link
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
    for i in range(len(under_armour_urls)):
        scrape_under_armour(under_armour_urls[i], COMPANY_NAME, clothing_styles[i])