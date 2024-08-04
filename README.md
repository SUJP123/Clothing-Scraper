# Clothing Site Scraper

# Introduction
This project involves web scraping several e-commerce websites, including Nike, Under Armour, Adidas, Puma, Forever 21, Lululemon, and Urban Outfitters. The goal is to extract product details such as names, prices, discounts, images, and links, and store them in a database for further analysis.

# Prerequisites
Before you begin, ensure you have met the following requirements:

- Python 3.7+
- requests library
- BeautifulSoup4 library
- selenium library
- SQLAlchemy library
- WebDriver for Selenium (ChromeDriver in this case)
- PostgreSQL (or any preferred database)
- Installation
  
# Clone the repository:

```bash
git clone https://github.com/yourusername/Clothing-Scraper.git
cd Clothing-Scraper
```

# Install the required Python packages:

```bash
pip install -r requirements.txt
```

# Set up the database:

``` bash
# Replace with your database setup commands
python setup_database.py
```


# Scraping Methodology
Utilize BeautifulSoups and Selenium or requests depending on the javascript present in the site. Additionally, some sites like Adidas require headers, and most of the sites need some type of scrolling to get all the products.

# Database Management
The project uses SQLAlchemy for ORM and database management.

# Contributing
Contributions are welcome! Please follow these steps to contribute:

# Fork the repository.
Create a new branch.
Make your changes and commit them.
Push to the branch.
Create a pull request.
License
This project is licensed under the MIT License. See the LICENSE file for more details.
