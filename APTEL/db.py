import asyncio
from contextlib import asynccontextmanager
from prisma import Prisma

class DatabaseConnection:
    def __init__(self):
        self.db = Prisma()
        self.connected = False

    async def connect(self):
        if not self.connected:
            await self.db.connect()
            self.connected = True

    async def disconnect(self):
        if self.connected:
            await self.db.disconnect()
            self.connected = False

    @asynccontextmanager
    async def get_connection(self):
        await self.connect()
        try:
            yield self.db
        finally:
            await self.disconnect()