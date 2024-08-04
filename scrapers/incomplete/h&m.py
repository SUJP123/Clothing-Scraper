import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# H&M URLs for scraping
hm_urls = ["https://www2.hm.com/en_us/men/sale/shirts.html"]
clothing_types = ["Men's Shirts"]

COMPANY_NAME = "h&m"

from models.product import Product, SessionLocal, reset_table
import requests
from bs4 import BeautifulSoup


def scrape_hm(url: str, company_name: str, clothing_type: str):
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

    # Parse the page source with BeautifulSoup
    req = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(req.content, 'html.parser')
    print(soup)

    products = []
    items = soup.find_all('li')

    for item in items:
        try:
            # Extract name while ignoring the span text
            name_tag = item.find('h2')
            if name_tag:
                name = name_tag.get_text(strip=True)

            # Extract deal price
            sale_price_element = item.find('span', class_='aeecde')
            deal = float(sale_price_element.text.strip()[2:]) if sale_price_element else None

            # Extract retail price
            price_element = item.find('span', class_='c04eed')
            retail = float(price_element.text.strip()[2:]) if price_element else None

            discount_percentage = (1 - (deal / retail)) * 100 if deal and retail else None
            saved = f"{discount_percentage:.2f}% off" if discount_percentage else None

            description = "Empty"

            # Extract image URL
            img_element = item.find('img', imagetype_='PRODUCT_IMAGE')
            image = img_element['src'] if img_element else "None"

            # Extract product link
            link_element = item.find('a', class_='db7c79')
            external_link = link_element['href'] if link_element else "None"

            print([name, deal, retail, saved, description, image, external_link, clothing_type])
            product = Product(
                name=name,
                retail=retail,
                deal=deal,
                saved=saved,
                company=company_name,
                description=description,
                clothing_type=clothing_type,
                image=image,
                external_link=external_link
            )

            products.append(product)
        except:
            print("Rrror parsing product info")

if __name__ == '__main__':
    for i in range(len(hm_urls)):
        scrape_hm(hm_urls[i], COMPANY_NAME, clothing_types[i])
