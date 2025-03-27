# extract_text.py
import pdfplumber
import re
import json
import os
import logging
from src.pdf_extraction.clean_text import clean_text, process_pdf
from pdfminer.high_level import extract_text
from PyPDF2 import PdfReader


logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

def load_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages or all(not page.extract_text() for page in pdf.pages):
                logging.error(f"Corrupted or unreadable PDF detected: {pdf_path}")
                return None
            return pdf
    except (pdfplumber.PDFSyntaxError, OSError, Exception) as e:
        logging.error(f"Error loading PDF {pdf_path}: {e}")
        return None

def extract_text_from_pdf(pdf_path, batch_size=5):
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    extracted_text = []

    for start in range(0, total_pages, batch_size):
        batch_text = ""
        for i in range(start, min(start + batch_size, total_pages)):
            batch_text += extract_text(pdf_path, page_numbers=[i]) + "\n\n"
        
        extracted_text.append(batch_text)
        yield batch_text  # Yield each batch instead of returning all at once


def identify_chapters(text):
    chapters = {}
    chapter_pattern = r'(Chapter \d+:.*?)\n(.*?)(?=Chapter \d+:|$)'
    matches = re.findall(chapter_pattern, text, re.DOTALL)
    for title, content in matches:
        chapters[title.strip()] = content.strip()
    return chapters

def save_to_json(data, output_file='processed_data.json'):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main(file, output_file='processed_data.json'):
    temp_pdf_path = "/tmp/uploaded_file.pdf"
    with open(temp_pdf_path, "wb") as f:
        f.write(file.read())

    pdf = load_pdf(temp_pdf_path)

    if pdf:
        extracted_text = extract_text_from_pdf(temp_pdf_path)
        cleaned_text = clean_text(extracted_text)
        chapters = identify_chapters(cleaned_text)
        save_to_json(chapters, output_file)
        return {"status": "success", "message": "Data successfully extracted.", "data": chapters}
    else:
        return {"status": "error", "message": "Failed to process PDF file. It may be corrupted or unreadable."}
