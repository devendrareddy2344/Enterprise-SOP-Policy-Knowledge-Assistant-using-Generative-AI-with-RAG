import streamlit as st
import requests

# =========================================
# Backend Configuration
# =========================================

BASE_URL = "http://127.0.0.1:8000"
ASK_URL = f"{BASE_URL}/ask"
UPLOAD_URL = f"{BASE_URL}/upload"

st.set_page_config(
    page_title="Enterprise Knowledge Assistant",
    page_icon="🏢",
    layout="wide"
)

# =========================================
# Session State Initialization
# =========================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = set()

# =========================================
# Backend Status Check
# =========================================

def check_backend():
    try:
        response = requests.get(BASE_URL)
        return response.status_code == 200
    except:
        return False

# =========================================
# Submit Query
# =========================================

def submit_query(question, role):
    try:
        payload = {
            "question": question,
            "role": role
        }

        with st.spinner("Analyzing knowledge base..."):
            response = requests.post(ASK_URL, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        st.error("Backend is unreachable. Please start FastAPI.")
        return None


# =========================================
# Sidebar
# =========================================

with st.sidebar:
    st.title("⚙️ Settings")

    role = st.selectbox(
        "Select User Role",
        ["HR", "Engineering", "Admin"]
    )

    st.divider()

    st.subheader("📡 Backend Status")

    if check_backend():
        st.success("Backend Online")
    else:
        st.error("Backend Offline")

    st.divider()

    st.subheader("📂 Upload Document")

    uploaded_file = st.file_uploader(
        "Upload TXT, CSV, or PDF",
        type=["txt", "csv", "pdf"]
    )

    # Upload only once per file
    if uploaded_file:
        if uploaded_file.name not in st.session_state.uploaded_files:

            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue())
            }

            try:
                with st.spinner("Uploading & indexing document..."):
                    response = requests.post(UPLOAD_URL, files=files)

                if response.status_code == 200:
                    st.success("Document uploaded & indexed successfully!")
                    st.session_state.uploaded_files.add(uploaded_file.name)
                else:
                    st.error("Upload failed.")

            except:
                st.error("Upload error. Check backend connection.")

    st.divider()

    # Optional Clear Chat Button
    if st.button("🗑 Clear Chat History"):
        st.session_state.chat_history = []
        st.success("Chat history cleared.")


# =========================================
# Main Chat Interface
# =========================================

st.title("🏢 Enterprise SOP & Policy Assistant")
st.markdown(
    "Ask questions about internal SOPs, policies, technical manuals, and compliance documents."
)

# =========================================
# Display Chat History
# =========================================

for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["question"])
        st.caption(f"Role: {chat['role']}")

    with st.chat_message("assistant"):
        st.write(chat["answer"])

        with st.expander("Details"):
            col1, col2 = st.columns(2)
            col1.metric("Confidence", f"{chat['confidence']}%")
            col2.metric("Response Time", f"{chat['response_time']}s")

            if chat["sources"]:
                st.write("Sources:")
                for source in chat["sources"]:
                    st.write(f"- {source}")

# =========================================
# Chat Input
# =========================================

question = st.chat_input("Ask a question about enterprise documents...")

if question:
    with st.chat_message("user"):
        st.write(question)
        st.caption(f"Role: {role}")

    result = submit_query(question, role)

    if result:
        answer = result.get("answer", "No answer")
        confidence = result.get("confidence", 0)
        response_time = result.get("response_time", 0)
        sources = result.get("sources", [])

        with st.chat_message("assistant"):
            st.write(answer)

            with st.expander("Details"):
                col1, col2 = st.columns(2)
                col1.metric("Confidence", f"{confidence}%")
                col2.metric("Response Time", f"{response_time}s")

                if sources:
                    st.write("Sources:")
                    for source in sources:
                        st.write(f"- {source}")

        # Save to chat history
        st.session_state.chat_history.append({
            "question": question,
            "role": role,
            "answer": answer,
            "confidence": confidence,
            "response_time": response_time,
            "sources": sources
        })
