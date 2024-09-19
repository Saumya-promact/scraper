import asyncio
from db_manager import DatabaseManager

db_manager = DatabaseManager()

async def update():
    await db_manager.update_fields()

asyncio.run(update())