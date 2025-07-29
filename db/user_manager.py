# your_project/db/user_manager.py

import sqlite3
import json
import time
import os # Added import for os in user_manager.py
from typing import Dict, Any, Optional

class UserManager:
    def __init__(self, db_path: str = 'data/users.db'):
        self.db_path = db_path
        self._ensure_db_dir()
        self._create_tables()

    def _ensure_db_dir(self):
        # Ensure the directory for the database exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def _get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # Allows accessing columns by name
        return conn

    def _create_tables(self):
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                is_verified BOOLEAN DEFAULT FALSE,
                role TEXT DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
