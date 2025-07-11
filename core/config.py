# core/config.py
import os
import psycopg2
from dotenv import load_dotenv
import logging
import time  # Ensure this exists
import streamlit as st

load_dotenv()

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def get_email_config():
    return {
        "smtp_server": st.secrets["email"]["smtp_server"],
        "smtp_port": st.secrets["email"]["smtp_port"],
        "email": st.secrets["email"]["email"],
        "password": st.secrets["email"]["password"]
    }

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
                port=os.getenv("DB_PORT", "5432"),
                connect_timeout=5,
                sslmode="require"
            )
            return conn
        except psycopg2.OperationalError as e:
            logging.warning(f"Connection attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                raise
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
