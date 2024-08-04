import os
import sys
import datetime
import traceback
import apprise
import psycopg2
from psycopg2 import sql
from selenium import webdriver
from datetime import datetime  
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from time import sleep
from dotenv import load_dotenv

load_dotenv()

RETAILERS = ['nike', 'adidas', 'under-armour', 'lululemon']

ALLOW_DUPLICATES = True if os.environ.get("ALLOW_DUPLICATES", "False").lower() == "true" else False

if os.environ.get("KEEP_ALIVE", "False").lower() == "true":
    from keep_alive import keep_alive
    keep_alive()
    KEEP_ALIVE = True
else:
    KEEP_ALIVE = False

# Set up Apprise, if enabled
APPRISE_ALERTS = os.environ.get("APPRISE_ALERTS", None)
if APPRISE_ALERTS:
    APPRISE_ALERTS = APPRISE_ALERTS.split(",")
    alerts = apprise.Apprise()
    for service in APPRISE_ALERTS:
        alerts.add(service)

# Database connection setup
def connect_db():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

def insert_promo(conn, description, code_required, promo_code, url, company):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO promos (description, code_required, promo_code, url, company) 
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING;
            """, (description, code_required, promo_code, url, company))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Failed to insert promo: {e}")
        print(traceback.format_exc())

def clear_table(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE promos;")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Failed to clear table: {e}")
        print(traceback.format_exc())

def getDriver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager(cache_valid_range=30).install()),
            options=chrome_options)
    except Exception as e:
        driver = webdriver.Chrome(options=chrome_options)
    return driver

def cached_codes_init():
    if not os.path.isfile("codes.txt"):
        open("codes.txt", "a").close()
        print(f"Created new codes.txt file")
    else:
        with open("codes.txt", "r") as f:
            if datetime.now().day == 1 and f.readlines():
                print("It's the first day of the month. Clearing the codes.txt file.")
                with open("codes.txt", "w"):    pass
            else:
                print(f"codes.txt file already exists")

def check_cached_codes(code):
    with open("codes.txt") as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
        if f"{str(code)}\n" in lines:
            print(f"Code {code} found in cache")
            return True
        return False

def append_cached_code(code):
    with open("codes.txt", "a") as f:
        f.write(f"{code}\n")
        print(f"Appended {code} to codes.txt")

def main():
    if not ALLOW_DUPLICATES:
        cached_codes_init()

    conn = connect_db()
    clear_table(conn)  # Clear the table at the beginning of each run
    driver = getDriver()

    for type in RETAILERS:
        print(f'{"-" * 70}\nRetrieving {type.upper()} Promo Code Offers...\n')
        driver.get(f'https://www.wired.com/coupons/{type}')

        coupons = (driver.find_element(By.CLASS_NAME, 'coupons-list')).find_elements(By.TAG_NAME, 'a')
        ids = [coupon.get_attribute('href') for coupon in coupons]

        print(f'{len(coupons)} {type.upper()} Promo Codes/Coupons were found!')
        
        for id in ids:
            driver.get(id)
            driver.refresh()
            try:
                sleep(2)
                print('-' * 50)
                title = driver.find_element(By.XPATH, '//*[@id="my-modal"]/div/div/div/h3')
                code = driver.find_element(By.XPATH, '//*[@id="my-modal"]/div/div/div/div[2]/span')
                try:
                    link = (driver.find_element(By.CLASS_NAME, 'modal-clickout__link')).get_attribute("href")
                except:
                    link = "(Error retrieving link)"
                    print(traceback.format_exc())

                description = title.text
                promo_code = code.text if code.text != "A CODE IS NOT REQUIRED" else None
                code_required = promo_code is not None

                print(f'{description}: {promo_code if promo_code else "No code required"} - {link}')

                if APPRISE_ALERTS:
                   alerts.notify(title=f'{type.upper()} Coupon', body=f'{description}\n\n{promo_code if promo_code else "No code required"}\n{link}')

                if not ALLOW_DUPLICATES:
                    if check_cached_codes(description):
                        print(f"Code {promo_code} for {description} already exists in cache, skipping")
                        continue
                    else:
                        append_cached_code(description)

                insert_promo(conn, description, code_required, promo_code, link, type)

            except:
                print(traceback.format_exc())
            finally:
                print('-' * 50)
        print(f'{"-" * 70}\nFinished retrieving promotions.\n{"-" * 70}')
    
    conn.close()

if __name__ == '__main__':
    if not KEEP_ALIVE:
        main()
    else:
        while True:
            main()
            sleep(3600)
