"""
Database migration script to add new fields to pickup_requests table.
Run this script to update existing database schema.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("development.db")


def migrate_database():
    """Add new fields to pickup_requests table if they don't exist."""
    if not DB_PATH.exists():
        print(f"Database {DB_PATH} not found. Skipping migration.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns exist and add them if they don't
        cursor.execute("PRAGMA table_info(pickup_requests)")
        columns = {col[1] for col in cursor.fetchall()}
        
        migrations = [
            ("storage", "TEXT"),
            ("additional_info", "TEXT"),
            ("photos_json", "TEXT"),
        ]
        
        for column_name, column_type in migrations:
            if column_name not in columns:
                print(f"Adding column: {column_name}")
                cursor.execute(f"ALTER TABLE pickup_requests ADD COLUMN {column_name} {column_type}")
            else:
                print(f"Column {column_name} already exists, skipping.")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate_database()

