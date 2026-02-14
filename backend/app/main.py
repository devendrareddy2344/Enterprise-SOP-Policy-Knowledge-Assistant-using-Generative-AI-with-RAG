import os
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
load_dotenv(dotenv_path=ENV_PATH)

# --------------------------------------------------
# Import RAG Functions
# --------------------------------------------------

from app.rag_pipeline import process_query, add_documents, load_vector_store

# --------------------------------------------------
# FastAPI App
# --------------------------------------------------

app = FastAPI(
    title="Enterprise Knowledge Assistant API",
    version="2.1 (Persistent FAISS Edition)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Startup Event (LOAD FAISS INDEX)
# --------------------------------------------------

@app.on_event("startup")
def startup_event():
    load_vector_store()
    print("🚀 Backend Ready. FAISS loaded if available.")


# --------------------------------------------------
# Request Model
# --------------------------------------------------

class QueryRequest(BaseModel):
    question: str
    role: str


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/")
def health_check():
    return {
        "status": "Backend running",
        "time": datetime.utcnow()
    }


# --------------------------------------------------
# Ask Endpoint
# --------------------------------------------------

@app.post("/ask")
async def ask_question(request: QueryRequest):
    try:
        start_time = time.time()

        result = process_query(request.question, request.role)

        response_time = round(time.time() - start_time, 2)

        return {
            "answer": result.get("answer"),
            "confidence": result.get("confidence"),
            "response_time": response_time,
            "sources": result.get("sources", [])
        }

    except Exception as e:
        print("ASK ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------
# Upload Endpoint
# --------------------------------------------------

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        filename = file.filename.lower()
        content = await file.read()

        # TXT
        if filename.endswith(".txt"):
            text = content.decode("utf-8")

        # CSV
        elif filename.endswith(".csv"):
            import pandas as pd
            from io import StringIO

            csv_data = StringIO(content.decode("utf-8"))
            df = pd.read_csv(csv_data)
            text = df.to_string()

        # PDF
        elif filename.endswith(".pdf"):
            from pypdf import PdfReader
            from io import BytesIO

            pdf_reader = PdfReader(BytesIO(content))
            text = ""

            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Only TXT, CSV, PDF allowed."
            )

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in document."
            )

        add_documents(file.filename, text)

        return {
            "message": f"{file.filename} uploaded and indexed successfully"
        }

    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
