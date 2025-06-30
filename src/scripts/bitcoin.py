import requests
import time
import psycopg2
import os
import yfinance as yf
from dotenv import load_dotenv
from decimal import Decimal, ROUND_HALF_UP

load_dotenv()

# Database connection parameters
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def bitcoin_price():
    btc = yf.Ticker("BTC-USD")
    price = btc.history(period="1d")["Close"].iloc[-1]
    price = Decimal(price)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    return price, timestamp


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
            CREATE TABLE IF NOT EXISTS bitcoin_price (
                id SERIAL PRIMARY KEY,
                price DECIMAL(20, 6) NOT NULL,
                timestamp TIMESTAMP NOT NULL
                )
            """)
        conn.commit()
        cursor.close()
        print("Database setup completed successfully.")
    except Exception as e:
        print(f"Error setting up database: {e}")

def save_to_database(price, timestamp, table_name='bitcoin_price'):
    """Saves the bitcoin price to the database."""
    print("Saving data to database...")
    try:
        cursor = conn.cursor()
        print(f"Inserting data: Price USD: {price}, Timestamp: {timestamp}")
        cursor.execute(f"""
            INSERT INTO {table_name} (price, timestamp) VALUES (
                {price}, '{timestamp}'
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

    while True:
        price, timestamp = bitcoin_price()
        save_to_database(price, timestamp)
        wait_time = 60 * 5  # Wait for 5 minutes before the next fetch
        print(f"Waiting for {wait_time} seconds before the next fetch...")
        time.sleep(wait_time)