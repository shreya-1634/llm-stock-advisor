import time
import psycopg2
import os
from dotenv import load_dotenv
import logging

load_dotenv()

def get_logger(name):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(name)

def get_db_connection():
    """Secure PostgreSQL connection with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT"),
                connect_timeout=5
            )
            return conn
        except psycopg2.OperationalError as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"Database connection failed after {max_retries} attempts: {str(e)}")
            logging.warning(f"Retrying database connection (attempt {attempt + 1})...")
            time.sleep(2)

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
