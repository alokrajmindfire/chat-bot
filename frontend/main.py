import streamlit as st
import requests
import time

API_BASE_URL = "http://127.0.0.1:8000"
UPLOAD_URL = f"{API_BASE_URL}/documents/upload"
QUERY_URL = f"{API_BASE_URL}/query/"
HEALTH_URL = f"{API_BASE_URL}/health"

st.set_page_config(page_title="Gemini RAG Chat", page_icon="A", layout="wide")

st.markdown("""
<style>
.chat-container {
    background-color: #0e1117;
    padding: 1rem;
    border-radius: 10px;
}
.answer-box {
    background-color: #1b1d35;
    padding: 0.8rem;
    border-radius: 10px;
    margin-top: 0.5rem;
}
.user-box {
    background-color: #0f1128;
    padding: 0.8rem;
    border-radius: 10px;
    margin-top: 0.5rem;
}
.source-expander {
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(int(time.time()))

if "query_input" not in st.session_state:
    st.session_state.query_input = ""

if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False

st.sidebar.title("📂 Document Upload")

uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file and not st.session_state.pdf_uploaded:
    with st.spinner("📄 Uploading & Processing PDF..."):
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        try:
            resp = requests.post(UPLOAD_URL, files=files)
            if resp.status_code == 200:
                st.sidebar.success("✅ PDF uploaded successfully!")
                st.session_state.pdf_uploaded = True
            else:
                st.sidebar.error(f"❌ Upload failed: {resp.text}")
        except Exception as e:
            st.sidebar.error(f"🚨 Error: {e}")

if st.session_state.pdf_uploaded:
    st.sidebar.info("📄 PDF already uploaded. You can now chat!")

st.sidebar.markdown("---")
top_k = st.sidebar.slider("🔍 Top K Results", 1, 10, 3)
st.sidebar.markdown("Adjust retrieval depth")

st.title("🤖 Gemini RAG Chatbot")
st.markdown("Ask any question based on your uploaded PDFs.")

question = st.text_input(
    "💬 Your Question:",
    value=st.session_state.query_input,
    placeholder="e.g., What is AI?",
    key="query_input_box"
)

ask_btn = st.button("🚀 Send")

if ask_btn:
    if not st.session_state.pdf_uploaded:
        st.warning("⚠️ Please upload a PDF first.")
    elif not question.strip():
        st.warning("⚠️ Please enter a question.")
    else:
        st.session_state.chat_history.append({"role": "user", "text": question})
        st.session_state.query_input = ""
        st.rerun()

if st.session_state.chat_history and (
    len(st.session_state.chat_history) == 1 or
    st.session_state.chat_history[-1]["role"] == "user"
):
    latest_question = st.session_state.chat_history[-1]["text"]

    with st.container():
        st.markdown(f"<div class='user-box'>👤 <b>You:</b> {latest_question}</div>", unsafe_allow_html=True)
        answer_placeholder = st.empty()

    with st.spinner("🤖 Gemini is thinking..."):
        try:
            payload = {
                "question": latest_question,
                "top_k": top_k,
                "conversation_id": st.session_state.conversation_id,
                "use_memory": True,
            }
            resp = requests.post(QUERY_URL, json=payload, timeout=120)

            if resp.status_code == 200:
                data = resp.json()
                answer = data.get("answer", "No answer generated.")
                sources = data.get("sources", [])

                st.session_state.chat_history.append(
                    {"role": "assistant", "text": answer, "sources": sources}
                )

                answer_placeholder.markdown(
                    f"<div class='answer-box'>🤖 <b>Gemini:</b> {answer}</div>",
                    unsafe_allow_html=True,
                )

                if sources:
                    st.markdown("<div class='source-expander'></div>", unsafe_allow_html=True)
                    with st.expander("📘 View Sources"):
                        for i, src in enumerate(sources, start=1):
                            st.markdown(f"**Source {i}:** {src}")

            else:
                detail = resp.json().get("detail", "Unknown error")
                answer_placeholder.markdown(
                    f"<div class='answer-box'>❌ Query failed: {detail}</div>",
                    unsafe_allow_html=True,
                )

        except Exception as e:
            answer_placeholder.markdown(
                f"<div class='answer-box'>🚨 Connection Error: {e}</div>",
                unsafe_allow_html=True,
            )

if st.session_state.chat_history:
    st.markdown("---")
    with st.container():
        for entry in st.session_state.chat_history[:-2]:
            if entry["role"] == "user":
                st.markdown(f"<div class='user-box'>👤 <b>You:</b> {entry['text']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='answer-box'>🤖 <b>Gemini:</b> {entry['text']}</div>", unsafe_allow_html=True)
                if "sources" in entry and entry["sources"]:
                    with st.expander("📘 View Sources", expanded=False):
                        for i, src in enumerate(entry["sources"], start=1):
                            st.markdown(f"**Source {i}:** {src}")
