# backend/init_db.py
import asyncio
import sys
import os
from dotenv import load_dotenv
from sqlalchemy import text  # <-- ADD THIS IMPORT

# Load environment variables FIRST
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import database modules
from ..core.database import Base, engine

async def init_db():
    """Initialize PostgreSQL database by creating all tables"""
    print("Initializing PostgreSQL database...")
    
    try:
        async with engine.begin() as conn:
            # Optional: Drop all tables (for development/reset)
            print("Dropping existing tables...")
            await conn.run_sync(Base.metadata.drop_all)
            
            # Create all tables
            print("Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ PostgreSQL database tables created successfully!")
        
        # Show created tables - FIXED: Use text() for raw SQL
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
            tables = result.fetchall()
            print(f"Created tables: {[table[0] for table in tables]}")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db())