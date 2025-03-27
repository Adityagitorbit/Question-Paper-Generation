# clean_text.py
import pdfplumber
import re
import os
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import logging
from PIL import Image
from pdf2image import convert_from_path
import io
import pytesseract

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load CLIP model for image-text relevance checking
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def is_garbled_text(text):
    if not text or not text.strip():
        return True
    symbol_ratio = len(re.findall(r"[^a-zA-Z0-9\s]", text)) / len(text)
    return symbol_ratio > 0.3

def is_relevant_image(image, surrounding_text):
    try:
        inputs = processor(text=surrounding_text, images=image, return_tensors="pt", padding=True)
        outputs = model(**inputs)
        similarity_score = torch.cosine_similarity(outputs['image_embeds'], outputs['text_embeds']).item()
        return similarity_score > 0.3
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return False

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    text = re.sub(r'[^A-Za-z0-9.,?!\s]', '', text)  # Remove special characters
    return text.strip()



# Path to Tesseract executable (if not already in PATH)
# For Windows users, specify the path like this:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_images_from_pdf(pdf_path):
    """Extracts images from a PDF file for text extraction."""
    images = convert_from_path(pdf_path)
    
    img_data_list = []
    for img in images:
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_data_list.append({"stream": img_byte_arr.getvalue()})
    
    return img_data_list

def ocr_function(image):
    """Performs OCR on an image and extracts text."""
    return pytesseract.image_to_string(image)

def process_pdf(pdf_path):
    extracted_text = ""
    for img_data in extract_images_from_pdf(pdf_path):
        img = Image.open(io.BytesIO(img_data["stream"]))
        extracted_text += ocr_function(img) + "\n"

    # Save processed text to a file for faster loading
    text_file_path = os.path.join("data", "processed_data", "processed_text.txt")
    with open(text_file_path, "w", encoding="utf-8") as file:
        file.write(extracted_text)
    
    return extracted_text, text_file_path
