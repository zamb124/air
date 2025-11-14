import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"


def get_db_path():
    db_name = os.getenv("TEST_DB_NAME", "db.db")
    return DATA_DIR / db_name


DB_PATH = get_db_path()


def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            flight_id TEXT PRIMARY KEY,
            flight_number TEXT NOT NULL,
            destination TEXT,
            origin TEXT,
            scheduled_time TEXT,
            actual_time TEXT,
            status TEXT NOT NULL,
            gate TEXT,
            terminal TEXT,
            delay_minutes INTEGER,
            flight_type TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_flight_type ON flights(flight_type)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_updated_at ON flights(updated_at)
    """)
    
    conn.commit()
    conn.close()


def get_db_connection():
    db_path = get_db_path()
    return sqlite3.connect(str(db_path), check_same_thread=False)

