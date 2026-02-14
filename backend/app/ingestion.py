import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

DATA_PATH = "data/documents"
VECTOR_PATH = "vector_store"

def load_documents():
    documents = []

    if not os.path.exists(DATA_PATH):
        return []

    for filename in os.listdir(DATA_PATH):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(DATA_PATH, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        department = "HR" if "hr" in filename.lower() else "Engineering"

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": filename,
                    "department": department
                }
            )
        )

    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    return splitter.split_documents(documents)


def rebuild_vector_store():
    documents = load_documents()

    if not documents:
        return

    split_docs = split_documents(documents)

    embeddings = OpenAIEmbeddings()

    vector_store = FAISS.from_documents(split_docs, embeddings)

    os.makedirs(VECTOR_PATH, exist_ok=True)
    vector_store.save_local(VECTOR_PATH)
