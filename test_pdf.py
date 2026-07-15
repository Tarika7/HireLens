from app.utils.pdf_extractor import extract_text_from_pdf

text = extract_text_from_pdf(
    "uploads/resumes/07bd9a41-72c8-4023-97e9-c934cf5a46a9.pdf"
)

print(text)