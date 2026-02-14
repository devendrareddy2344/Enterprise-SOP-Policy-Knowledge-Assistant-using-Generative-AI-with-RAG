from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import os

VECTOR_PATH = "vector_store"

def load_vector_store():
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(VECTOR_PATH, embeddings, allow_dangerous_deserialization=True)

def retrieve_documents(query, role, k=3):
    if not os.path.exists(VECTOR_PATH):
        return [], []

    vector_store = load_vector_store()
    results = vector_store.similarity_search_with_score(query, k=k)

    docs = []
    scores = []

    for doc, score in results:
        if role == "Admin" or doc.metadata.get("department") == role:
            docs.append(doc)
            similarity = 1 - score
            scores.append(similarity)

    return docs, scores
