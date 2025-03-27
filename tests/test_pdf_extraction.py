import pytest
import json
import re
from src.pdf_extraction.extract_text import (
    load_pdf,
    extract_text_from_pdf,
    clean_text,
    identify_chapters,
    save_to_json
)

# Sample PDF Paths
SAMPLE_TEXT_PDF = "/home/aditya/Programs/Git_HUB/Question-Paper-Generation/data/sample_pdfs/sample_text.pdf"
SAMPLE_IMAGE_PDF = "/home/aditya/Programs/Git_HUB/Question-Paper-Generation/data/sample_pdfs/sample_with_images.pdf"
CORRUPTED_PDF = "/home/aditya/Programs/Git_HUB/Question-Paper-Generation/data/sample_pdfs/corrupted.pdf"

# ---------- TEST CASES ----------

def test_load_pdf_valid():
    """Test if a valid PDF is loaded successfully."""
    pdf = load_pdf(SAMPLE_TEXT_PDF)
    assert pdf is not None



def test_load_pdf_invalid():
    """Test if loading an invalid/corrupted PDF raises an error or produces no meaningful text."""
    pdf = load_pdf(CORRUPTED_PDF)
    
    def is_garbled_text(text):
        if not text or not text.strip():  # Handle None and empty content
            return True
        # Identify garbled text by checking symbol-to-text ratio
        symbol_ratio = len(re.findall(r"[^a-zA-Z0-9\s]", text)) / len(text)
        error_keywords = ["error", "404", "%%", "randomsymbols"]
        contains_error_keywords = any(keyword.lower() in text.lower() for keyword in error_keywords)
        return symbol_ratio > 0.3 or contains_error_keywords  # Enhanced condition

    assert (
        pdf is None
        or len(pdf.pages) == 0
        or all(is_garbled_text(page.extract_text() or "") for page in pdf.pages)
    )




def test_extract_text():
    """Test if text is correctly extracted from a sample PDF."""
    text = extract_text_from_pdf(SAMPLE_TEXT_PDF)  # Pass path directly
    assert "Introduction to Science" in text  # Known content in sample PDF


def test_clean_text():
    """Test text cleaning logic for unwanted noise."""
    sample_text = """
        1. Introduction to Science
        Page 23
        The study of matter and energy.
        
        Chapter 2
        Properties of Matter
        """
    cleaned_text = clean_text(sample_text)
    assert "Page 23" not in cleaned_text
    assert "Introduction to Science" in cleaned_text
    assert "Properties of Matter" in cleaned_text

def test_identify_chapters():
    """Test chapter identification logic."""
    sample_text = """
    Chapter 1: Introduction to Biology
    Biology is the study of life.

    Chapter 2: Cells
    Cells are the building blocks of life.
    """
    chapters = identify_chapters(sample_text)
    assert "Chapter 1: Introduction to Biology" in chapters
    assert "Chapter 2: Cells" in chapters
    assert "Cells are the building blocks of life." in chapters["Chapter 2: Cells"]

def test_save_to_json(tmp_path):
    """Test if extracted data is saved correctly in JSON format."""
    sample_data = {
        "Chapter 1": "Introduction to Biology",
        "Chapter 2": "Cells and Their Structure"
    }
    output_file = tmp_path / "output.json"
    save_to_json(sample_data, str(output_file))

    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert data == sample_data
