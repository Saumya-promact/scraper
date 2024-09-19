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
                    "coram": case_info['judges'],
                    "petitioner": case_info['petitioner'],
                    "respondent": case_info['respondent'],
                    "caseno": case_info['case_number'],
                    "pdf_link": case_info.get('pdf_link', ''),
                    "filename": case_info.get('filename', ''),
                    "dated": case_info['date'],
                    "court": "Sikkim High Court"
                })
                print(f"Stored metadata in database with ID: {metadata.id}")
                self.logger.log_success(f"Successfully stored metadata with ID: {metadata.id}. Data: {case_info}")
            except Exception as e:
                print(f"Error storing metadata in database: {str(e)}")
    
    async def update_abbr(self):
        async with self.db_connection.get_connection() as db:
            try:
                updated_count = await db.metadata.update_many(
                    where={},
                    data={
                        "abbr": "SIK"
                    }
                )
                print(f"Successfully updated {updated_count} records.")
            except Exception as e:
                print(f"Error updating in database: {str(e)}")
    
    async def update_fields(self):
        async with self.db_connection.get_connection() as db:
            try:
                records = await db.metadata.find_many()
                update_count = 0
                for record in records:
                    coram_count = len(record.coram) if hasattr(record, "coram") else 0
                    case_name = record.petitioner + r'v/s' + record.respondent
                    await db.metadata.update(
                        where={"filename": record.filename},
                        data={
                            "coram_count": coram_count,
                            "casename" : case_name
                        }
                    )
                    update_count += 1
                
                print(f"Successfully updated {update_count} records.")
            except Exception as e:
                print(f"Error updating in database: {str(e)}")


    @asynccontextmanager
    async def get_connection(self):
        async with self.db_connection.get_connection() as db:
            yield db