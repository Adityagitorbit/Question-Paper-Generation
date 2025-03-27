from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

from src.pdf_extraction.extract_text import extract_text_from_pdf
from src.pdf_extraction.clean_text import clean_text

app = FastAPI()
UPLOAD_DIR = "data/processed_data"
templates = Jinja2Templates(directory="src/app/templates")


@app.get("/upload/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload/", response_class=HTMLResponse)
async def upload(request: Request, file: UploadFile = File(...)):
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    processed_text_path = file_path.replace(".pdf", "_processed.txt")

    # Open the text file for writing in append mode
    with open(processed_text_path, "w") as text_file:
        processed_text = ""

        # Extract and clean text in batches
        for batch_text in extract_text_from_pdf(file_path, batch_size=5):
            cleaned_batch = clean_text(batch_text)
            processed_text += cleaned_batch + "\n\n"
            text_file.write(cleaned_batch + "\n\n")  # Append cleaned text to the file

    # Render the template with the processed text
    return templates.TemplateResponse(
        "upload_result.html",
        {"request": request, "filename": file.filename, "processed_text": processed_text}
    )
