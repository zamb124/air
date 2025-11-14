import aiosqlite
import os
from pathlib import Path

DB_DIR = Path(__file__).parent


def get_db_path():
    db_name = os.getenv("TEST_DB_NAME", "db.db")
    return DB_DIR / db_name


DB_PATH = get_db_path()


async def init_db():
    db_path = get_db_path()
    
    async with aiosqlite.connect(str(db_path)) as conn:
        await conn.execute("""
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
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_flight_type ON flights(flight_type)
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_updated_at ON flights(updated_at)
        """)
        
        await conn.commit()


async def get_db_connection():
    db_path = get_db_path()
    return await aiosqlite.connect(str(db_path))
