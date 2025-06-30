import time
import os
import yfinance as yf
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Carrega variáveis do .env
load_dotenv()

# Parâmetros do banco
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Criação da engine (uso compartilhado)
engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def bitcoin_price():
    """Busca o preço atual do Bitcoin e retorna com timestamp."""
    btc = yf.Ticker("BTC-USD")
    price = btc.history(period="1d")["Close"].iloc[-1]
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    return price, timestamp

def setup_database():
    """Cria a tabela no banco, se ainda não existir."""
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS bitcoin_price (
                id SERIAL PRIMARY KEY,
                price DECIMAL(20, 6) NOT NULL,
                timestamp TIMESTAMP NOT NULL
            )
        """))
    print("Database setup completed.")

def save_to_database(price, timestamp):
    """Salva o preço do Bitcoin no banco."""
    price = round(float(price), 6)

    try:
        with engine.connect() as connection:
            print(f"Inserindo dados: price={price}, timestamp={timestamp}")
            connection.execute(
                text("INSERT INTO bitcoin_price (price, timestamp) VALUES (:price, :timestamp)"),
                {"price": price, "timestamp": timestamp}
            )
            print("Dados salvos com sucesso.")
    except Exception as e:
        print(f"Erro ao salvar no banco de dados: {e}")

if __name__ == "__main__":
    setup_database()
    while True:
        price, timestamp = bitcoin_price()
        save_to_database(price, timestamp)
        wait_time = 60 * 5  # 5 minutos
        print(f"Aguardando {wait_time} segundos para a próxima coleta...")
        time.sleep(wait_time)
