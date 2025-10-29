"""
Simple test script to verify the database setup is working correctly.
Run this after installing dependencies to test your setup.
"""

from app.db.database import create_db_and_tables

if __name__ == "__main__":
    print("Testing database initialization...")
    try:
        create_db_and_tables()
        print("\n✅ Setup test successful! Your database is ready to use.")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print("Please check the error message above and ensure all dependencies are installed.")

