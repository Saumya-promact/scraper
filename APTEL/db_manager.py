from contextlib import asynccontextmanager
from prisma import Prisma
from logger import Logger


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




class DatabaseManager:
    def __init__(self):
        self.db_connection = DatabaseConnection()
        self.logger = Logger()

    async def store_metadata(self, case_info):
        async with self.db_connection.get_connection() as db:
            try:
                metadata = await db.metadata.create(data={
                    "petitioner": case_info['petitioner'],
                    "respondent": case_info['respondent'],
                    "caseno": case_info['case_number'],
                    "pdf_link": case_info.get('pdf_link', ''),
                    "filename": case_info.get('filename', ''),
                    "dated": case_info['date'],
                    "court": "Appellate Tribunal for Electricity",
                    "casename": case_info['petitioner'] + ' Vs ' + case_info['respondent'],
                    "abbr": "APTEL"
                })
                self.logger.log_success(f"Successfully stored pdf with name: {metadata.filename}. Data: {case_info}")
            except Exception as e:
                print(f"Error storing metadata in database: {str(e)}")

    @asynccontextmanager
    async def get_connection(self):
        async with self.db_connection.get_connection() as db:
            yield db