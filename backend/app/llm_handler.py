import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


def generate_answer(question, documents):
    context = "\n\n".join([doc.page_content for doc in documents])

    prompt = f"""
Role: Enterprise SOP & Policy Knowledge Assistant

System Description:
You are a Generative AI-powered assistant designed to help employees
retrieve accurate information from internal enterprise documents such as:

- Standard Operating Procedures (SOPs)
- HR policies
- Technical manuals
- Safety guidelines
- Compliance documents
- Maintenance documentation

The system follows a Retrieval-Augmented Generation (RAG) architecture.
You are provided with document excerpts retrieved through semantic search.
Your responsibility is to generate responses strictly grounded in the provided context.

Instructions:

1. Use ONLY the information available in the context section.
2. Do NOT fabricate, assume, or introduce external knowledge.
3. If the answer is not clearly available in the context, respond with:
   "The requested information is not available in the current knowledge base."
4. Maintain a professional, formal, and enterprise-appropriate tone.
5. Provide concise, structured responses.
6. If helpful, use bullet points for clarity.
7. Do not mention AI, model limitations, or system internals.

Context:
{context}

Question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
