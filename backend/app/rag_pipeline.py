import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from app.llm_handler import generate_answer

# -----------------------------
# Global Variables
# -----------------------------
vector_store = None
INDEX_PATH = "faiss_index"


# -----------------------------
# Embeddings (Cloud-Based)
# -----------------------------
def get_embeddings():
    return HuggingFaceInferenceAPIEmbeddings(
        api_key=os.getenv("HF_TOKEN"),
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# -----------------------------
# Load Existing FAISS
# -----------------------------
def load_vector_store():
    global vector_store

    if os.path.exists(INDEX_PATH):
        embeddings = get_embeddings()
        vector_store = FAISS.load_local(
            INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("✅ FAISS index loaded from disk.")


# -----------------------------
# Save FAISS
# -----------------------------
def save_vector_store():
    global vector_store
    if vector_store:
        vector_store.save_local(INDEX_PATH)
        print("💾 FAISS index saved to disk.")


# -----------------------------
# Add Documents
# -----------------------------
def add_documents(filename, text):
    global vector_store

    department = "HR" if "hr" in filename.lower() else "Engineering"

    document = Document(
        page_content=text,
        metadata={
            "source": filename,
            "department": department
        }
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    split_docs = splitter.split_documents([document])
    embeddings = get_embeddings()

    if vector_store is None:
        if os.path.exists(INDEX_PATH):
            vector_store = FAISS.load_local(
                INDEX_PATH,
                embeddings,
                allow_dangerous_deserialization=True
            )
            vector_store.add_documents(split_docs)
        else:
            vector_store = FAISS.from_documents(split_docs, embeddings)
    else:
        vector_store.add_documents(split_docs)

    save_vector_store()


# -----------------------------
# Process Query
# -----------------------------
def process_query(question, role):
    global vector_store

    if vector_store is None:
        load_vector_store()

    if vector_store is None:
        return {
            "answer": "No documents uploaded yet.",
            "confidence": 0.0,
            "sources": []
        }

    results = vector_store.similarity_search_with_score(question, k=3)

    docs = []
    scores = []

    for doc, score in results:
        if role == "Admin" or doc.metadata.get("department") == role:
            docs.append(doc)
            similarity = float(1 / (1 + score))
            scores.append(similarity)

    if not docs:
        return {
            "answer": "Information not found in knowledge base.",
            "confidence": 0.0,
            "sources": []
        }

    avg_score = sum(scores) / len(scores)

    answer = generate_answer(question, docs)

    return {
        "answer": answer,
        "confidence": float(round(avg_score * 100, 2)),
        "sources": list(set([doc.metadata["source"] for doc in docs]))
    }
