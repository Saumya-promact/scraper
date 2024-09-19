import os


def list_pdf_files(pdf_directory):
    pdf_files = []
    for pdf_file in os.listdir(pdf_directory):
        if pdf_file.endswith(".pdf"):
            pdf_files.append(pdf_file)
    return pdf_files
