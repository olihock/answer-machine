import os
from PyPDF2 import PdfReader


def slice_to_pages(filename):
    pages = []
    with open(filename, mode="rb") as file_content:
        pdf_reader = PdfReader(file_content)
        for page in pdf_reader.pages:
            content = page.extract_text()
            pages.append(content)
    return pages


def slice_pdf_document(pdf_content):
    pages = []
    for page in pdf_content.pages:
        content = page.extract_text()
        pages.append(content)
    return pages


def read_custom_data(data_path):
    """
    Read PDF files and ignore all other file types. Insert read text
    page-wise into a list, so it can be dealt with by the caller.
    """
    page_texts = []
    for file in os.listdir(data_path):
        if file.endswith(".pdf"):
            file_path = os.path.join(data_path, file)
            print(file_path)
            with open(file_path, 'r'):
                reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            page_texts.append(page_text)
    return page_texts
