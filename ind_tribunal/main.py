import asyncio
from scraper import Scraper
from config import Config

async def main():
    config = Config()
    scraper = Scraper(config)
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())