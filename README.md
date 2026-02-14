# Enterprise Knowledge Assistant (RAG System)

This is a production-ready, RAG-based Enterprise Knowledge Assistant. It uses a strict separation of concerns between the **Streamlit Frontend** and the **FastAPI Backend**.

## Project Architecture

The system follows a microservice-like architecture:

1.  **Frontend (Streamlit)**:
    -   Handles User Interface (UI).
    -   Collects user queries and role selection.
    -   Sends HTTP POST requests to the Backend.
    -   **Does NOT** communicate with OpenAI directly.

2.  **Backend (FastAPI)**:
    -   Exposes a REST API (`/ask`).
    -   **RAG Pipeline**:
        -   **Ingestion**: Loading documents, splitting them into chunks, and creating vector embeddings.
        -   **Retrieval**: Searching the FAISS index for relevant context based on semantic similarity and user role.
        -   **Generation**: Using OpenAI GPT-3.5 Turbo to generate answers strictly from the retrieved context.
    -   **Logging**: Tracks queries, response times, and confidence scores in `backend/logs/query_logs.csv`.

## Folder Structure

```
enterprise-rag/
│
├── backend/                  # Backend Logic (FastAPI)
│   ├── app/
│   │   ├── main.py           # API Entry Point
│   │   ├── rag_pipeline.py   # RAG Logic Orchestrator
│   │   ├── ingestion.py      # Document Loading & Vectorization
│   │   ├── retrieval.py      # Semantic Search Engine
│   │   ├── llm_handler.py    # OpenAI Integration
│   │   ├── utils.py          # Logging & Helper Functions
│   │   └── __init__.py
│   │
│   ├── data/
│   │   └── documents/        # Place your knowledge base files here (TXT, CSV)
│   │
│   ├── vector_store/         # Persisted FAISS Index
│   ├── logs/                 # CSV Logs for analytics
│   ├── requirements.txt
│   └── .env
│
├── frontend/                 # Frontend Logic (Streamlit)
│   ├── streamlit_app.py      # Main UI Application
│   └── requirements.txt
│
└── README.md
```

## Setup Instructions

### 1. Prerequisites

-   Python 3.9+ installed and added to PATH.
-   An OpenAI API Key.

### 2. Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```

2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Create a `.env` file in the `backend` folder and add your OpenAI Key:
    ```env
    OPENAI_API_KEY=sk-your-key-here
    ```

5.  **Run the Backend**:
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```
    *The server will start at `http://127.0.0.1:8000`.*
    *On first run, it will automatically ingest sample documents created in `data/documents`.*

### 3. Frontend Setup

1.  Open a new terminal and navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```

2.  Create a virtual environment (optional):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Frontend**:
    ```bash
    streamlit run streamlit_app.py
    ```
    *The app will open in your browser at `http://localhost:8501`.*

## Deployment

### Deploy Backend (Render)

1.  Create a new **Web Service** on Render.
2.  Connect your repository.
3.  Set **Root Directory** to `backend`.
4.  Set **Build Command** to `pip install -r requirements.txt`.
5.  Set **Start Command** to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
6.  Add `OPENAI_API_KEY` in Environment Variables.

### Deploy Frontend (Streamlit Cloud)

1.  Push your code to GitHub.
2.  Go to Streamlit Cloud and deploy the app.
3.  Select `frontend/streamlit_app.py` as the main file.
4.  (Optional) Add `BACKEND_URL` to Secrets or Environment Variables if your backend URL differs from localhost.

## Features

-   **Role-Based Access Control**: Filter documents by Department (HR, Engineering, Admin).
-   **Hallucination Control**: If confidence is low (<70%), it explicitly states "Information not found".
-   **Logging**: All interactions are logged with timestamps and metrics.
-   **Modular Code**: Clean separation of ingestion, retrieval, and generation logic.
