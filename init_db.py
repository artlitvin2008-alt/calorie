"""
Initialize database script
"""
import asyncio
import logging
from core.database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Initialize database"""
    logger.info("Initializing database...")
    
    db = Database("data/database.db")
    await db.initialize()
    
    logger.info("✅ Database initialized successfully!")
    logger.info("Database location: data/database.db")
    
    # Show table count
    import aiosqlite
    async with aiosqlite.connect("data/database.db") as conn:
        async with conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ) as cursor:
            tables = await cursor.fetchall()
            logger.info(f"Created {len(tables)} tables:")
            for table in tables:
                logger.info(f"  - {table[0]}")


if __name__ == "__main__":
    asyncio.run(main())
