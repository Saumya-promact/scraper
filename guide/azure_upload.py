import requests
import logging
import time
import tempfile
from io import BytesIO
from db import update_record_process, update_bombay_hc_record_process


def upload_to_azure(pdf_links, container_name):
    try:
        # Upload iteratively
        for pdf_link in pdf_links:
            response = requests.get(pdf_link)
            if response.status_code == 200:
                file_name = pdf_link.split("/")[-1]
                pdf_content = response.content

                container_name.upload_blob(file_name, BytesIO(pdf_content))

                print(f"Uploaded {file_name} to Azure blob container.")
                update_record_process(pdf_link)
            else:
                logging.error(f"Failed to download {pdf_link}")

        logging.info("Successfully uploaded all PDFs to Azure blob container")
        print("Successfully uploaded all PDFs to Azure blob container")
    except Exception as e:
        logging.error(f"Error in uploading files with exception = {e}")
        print(e)


def upload_bhc_pdf_to_azure(url, container_client):
    try:
        # Attempt direct download using requests
        timestamp = int(time.time())

        # Save the PDF file directly to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_pdf_file:
            direct_response = requests.get(url, stream=True)
            direct_response.raise_for_status()
            for chunk in direct_response.iter_content(chunk_size=8192):
                temp_pdf_file.write(chunk)

        # Upload the temporary PDF file to Azure Blob Storage
        with open(temp_pdf_file.name, "rb") as local_file:
            blob_name = f"BLA_BHC_{timestamp}.pdf"  # Generate a unique name
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(local_file, overwrite=True)

        # Update the database record to "Uploaded" and set the pdf name in pdf column
        update_bombay_hc_record_process(url, blob_name)

        print(f"PDF uploaded to Azure Blob Storage: {blob_name}")

    except requests.exceptions.RequestException as direct_error:
        print(direct_error)
