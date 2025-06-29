import requests
import time
import psycopg2
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

# Database connection parameters
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def fetch_page(url):
    """Fetches the HTML content of the given URL."""
    response = requests.get(url)
    print(f"Fetching URL")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        return response.text
    return None

def parse_page(html_content):
    """Parses the HTML content and extracts product information."""
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    for item in soup.find_all('li', class_='ui-search-layout__item'):
        title = item.find('a', class_= 'poly-component__title').get_text(strip=True)
        title = title.replace('Apple ', '')
        title = title.replace(' - Distribuidor Autorizado', '')
        prices = item.find_all('span', class_='andes-money-amount__fraction')
        price = int(prices[1].get_text(strip=True).replace('.', ''))
        installment_price = int(prices[2].get_text(strip=True).replace('.', ''))

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        products.append({'title': title, 'price': price, 'installment_price': installment_price, 'timestamp': timestamp})
    return products

def create_connection():
    """Creates a connection to the PostgreSQL database."""
    print("Creating database connection...")
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    print("Database connection established.")
    return conn

def setup_database(conn):
    """Sets up the database by creating the necessary table."""
    print("Setting up database...")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                price INTEGER NOT NULL,
                installment_price INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL
                )
            """)
        conn.commit()
        cursor.close()
        print("Database setup completed successfully.")
    except Exception as e:
        print(f"Error setting up database: {e}")

def save_to_database(products, table_name='products'):
    """Saves the extracted product data to the database."""
    print("Saving data to database...")
    try:
        cursor = conn.cursor()
        for product in products:
            print(f"Inserting product: {product['title']}, Price: {product['price']}, Installment Price: {product['installment_price']}, Timestamp: {product['timestamp']}")
            cursor.execute(f"""
                INSERT INTO {table_name} (title, price, installment_price, timestamp) VALUES (
                    '{product['title']}', {product['price']}, {product['installment_price']}, '{product['timestamp']}'
                )
            """)
        conn.commit()
        cursor.close()
        print("Data saved to database successfully.")
    except Exception as e:
        print(f"Error saving to database: {e}")


if __name__ == "__main__":
    conn = create_connection()
    setup_database(conn)

    url = "https://lista.mercadolivre.com.br/celulares-telefones/celulares-smartphones/iphone-16/_Loja_apple#applied_filter_id%3DMODEL%26applied_filter_name%3DModelo%26applied_filter_order%3D11%26applied_value_id%3D41954949%26applied_value_name%3DiPhone+16%26applied_value_order%3D8%26applied_value_results%3D4%26is_custom%3Dfalse"
    data = fetch_page(url)

    if data:
        print("Data fetched successfully.")
        products = parse_page(data)
        if products:
            print(f"Found {len(products)} products.")
            save_to_database(products)
        else:
            print("No products found.")
    else:
        print("No data fetched.")