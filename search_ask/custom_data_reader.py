import os
from PyPDF2 import PdfReader


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


custom_data = run("data")
print(custom_data.__len__())
