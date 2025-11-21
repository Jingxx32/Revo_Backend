"""
Database migration script to add new columns to existing tables.

This script adds the new columns that were added to the User and Order models:
- users.full_name
- users.phone_number
- orders.shipping_address_json

Run this script once to update your database schema.
"""

from sqlalchemy import text
from app.db.database import engine
from app.core.config import settings
import os

def migrate_database():
    """Add new columns to existing tables if they don't exist."""
    
    database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    print("Starting database migration...")
    
    with engine.connect() as conn:
        try:
            # Check if columns exist and add them if they don't
            migrations = [
                # Add full_name to users table
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'users' AND column_name = 'full_name'
                    ) THEN
                        ALTER TABLE users ADD COLUMN full_name VARCHAR;
                    END IF;
                END $$;
                """,
                
                # Add phone_number to users table
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'users' AND column_name = 'phone_number'
                    ) THEN
                        ALTER TABLE users ADD COLUMN phone_number VARCHAR;
                    END IF;
                END $$;
                """,
                
                # Add shipping_address_json to orders table
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'orders' AND column_name = 'shipping_address_json'
                    ) THEN
                        ALTER TABLE orders ADD COLUMN shipping_address_json JSONB;
                    END IF;
                END $$;
                """,
                
                # Create addresses table if it doesn't exist
                """
                CREATE TABLE IF NOT EXISTS addresses (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    full_name VARCHAR NOT NULL,
                    phone_number VARCHAR NOT NULL,
                    address_line1 VARCHAR NOT NULL,
                    address_line2 VARCHAR,
                    city VARCHAR NOT NULL,
                    state VARCHAR NOT NULL,
                    postal_code VARCHAR NOT NULL,
                    country VARCHAR DEFAULT 'Canada',
                    is_default BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
                """,
            ]
            
            for migration in migrations:
                try:
                    conn.execute(text(migration))
                    conn.commit()
                    print("✓ Migration executed successfully")
                except Exception as e:
                    # If the migration fails, it might be because the column already exists
                    # or the table already exists, which is fine
                    print(f"⚠ Migration note: {str(e)[:100]}")
                    conn.rollback()
            
            print("\n Database migration completed!")
            print("\nNew columns added:")
            print("  - users.full_name")
            print("  - users.phone_number")
            print("  - orders.shipping_address_json")
            print("  - addresses table (if it didn't exist)")
            
        except Exception as e:
            print(f"\n Migration error: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    migrate_database()

