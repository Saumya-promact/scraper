import os
from datetime import datetime
from dotenv import load_dotenv
from Base import get_previous_week_dates
from azure.storage.blob import BlobServiceClient
from supreme_court_weekly import crawl_sc_weekly
from db import get_scrapped_records
from azure_upload import upload_to_azure
from bombay_highcourt import crawl_bombay_highcourt
from gujarat_hc_weekly import crawl_gj_hc_batch_wise

load_dotenv()


if __name__ == "__main__":
    start_date, end_date = get_previous_week_dates(datetime.now())

    AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

    # Initialize Azure blob client
    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_STORAGE_CONNECTION_STRING
    )
    container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

    # Crawling Supreme Court
    crawl_sc_weekly(start_date, end_date)

    # Crawling Bombay High Court
    crawl_bombay_highcourt(container_client, start_date, end_date)

    # Fetch the remaining PDFs from the database
    all_pdf_links = get_scrapped_records()
    if all_pdf_links:
        upload_to_azure(all_pdf_links, container_client)
        print(f"{len(all_pdf_links)} - PDFs uploaded")

    # Crawling Gujarat High Court
    crawl_gj_hc_batch_wise(container_client)
    print("Scrapping completed for both courts")
