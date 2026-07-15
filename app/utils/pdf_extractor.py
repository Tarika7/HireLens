import fitz


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF using PyMuPDF.
    """

    document = fitz.open(pdf_path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text