import pdfplumber
from docx import Document
from fastapi import UploadFile


def extract_text_from_resume_file(resume: UploadFile) -> str:
    try:
        resume.file.seek(0)

        if resume.filename.lower().endswith(".pdf"):
            return extract_pdf_text_advanced(resume)
        elif resume.filename.lower().endswith(".docx"):
            return extract_docx_text(resume)
        else:
            return ""
    except Exception as e:
        print(f"Error extracting resume text: {e}")
        return ""


def extract_pdf_text_advanced(upload_file: UploadFile) -> str:
    upload_file.file.seek(0)
    text = ""
    try:
        with pdfplumber.open(upload_file.file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"PDF extraction error: {e}")
    return text.strip()


def extract_docx_text(upload_file: UploadFile) -> str:
    text = ""
    try:
        doc = Document(upload_file.file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"DOCX extraction error: {e}")
    return text.strip()
