from fastapi import APIRouter, UploadFile, File
from src.pdf_extraction.extract_text import extract_text_from_pdf, identify_chapters, save_to_json
from src.pdf_extraction.clean_text import process_pdf
import os
import shutil

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/process-pdf/")
async def process_pdf_route(file: UploadFile = File(...)):
    # Save uploaded file
    temp_pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(temp_pdf_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Clean text and filter images
    cleaned_text = process_pdf(temp_pdf_path, output_folder="filtered_images")
    if not cleaned_text:
        return {"status": "error", "message": "Failed to extract meaningful text."}

    # Identify chapters
    chapters = identify_chapters(cleaned_text)
    json_output_path = os.path.join(UPLOAD_FOLDER, "processed_data.json")
    save_to_json(chapters, json_output_path)

    return {
        "status": "success",
        "message": "PDF processed successfully.",
        "json_output": json_output_path
    }
