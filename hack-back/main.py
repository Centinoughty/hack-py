from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from transformers import pipeline
import uvicorn
import os
import tempfile
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("APIKEY")
MODEL_NAME = os.getenv("MODELNAME")

# Configure Google Generative AI
genai.configure(api_key=API_KEY)

app = FastAPI()

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        return text
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {e}")

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF and extract its content."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file.file.read())
            text = extract_text_from_pdf(tmp_file.name)
        return JSONResponse(content={"text": text})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/ask-genai")
async def ask_genai_question(prompt: str):
    """Ask a question using Google Generative AI."""
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt must be provided.")
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return JSONResponse(content={"response": response.text})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Notes Generation API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
