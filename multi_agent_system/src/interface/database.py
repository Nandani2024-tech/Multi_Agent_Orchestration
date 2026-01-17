import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class DatabaseHandler:
    def __init__(self, db_path: str = "orchestrator.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Creates the necessary tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table 1: Long-term Memory (Key-Value Store)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP
            )
        ''')
        
        # Table 2: Audit Logs (Record everything agents do)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                agent_id TEXT,
                action TEXT,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    # --- MEMORY OPERATIONS ---
    
    def save_memory(self, key: str, value: str):
        """Upsert (Update or Insert) a memory item."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO memory (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.now()))
        conn.commit()
        conn.close()

    def get_memory(self, key: str) -> str:
        """Retrieves a specific memory item."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM memory WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def get_all_memory(self) -> Dict[str, str]:
        """Returns all memory as a dictionary."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM memory')
        rows = cursor.fetchall()
        conn.close()
        return {row[0]: row[1] for row in rows}

    # --- LOGGING OPERATIONS (Bonus Feature) ---

    def log_event(self, agent_id: str, action: str, details: str):
        """Records an event for debugging/auditing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (timestamp, agent_id, action, details)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now(), agent_id, action, details))
        conn.commit()
        conn.close()

# Singleton Instance
db = DatabaseHandler()