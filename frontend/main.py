import streamlit as st
import requests
import time

API_BASE_URL = "http://127.0.0.1:8000"
UPLOAD_URL = f"{API_BASE_URL}/documents/upload"
QUERY_URL = f"{API_BASE_URL}/query/"
HEALTH_URL = f"{API_BASE_URL}/health"

st.set_page_config(
    page_title="📚 RAG PDF Q&A with Gemini",
    page_icon="📚",
    layout="centered",
)

st.markdown("""
<style>
h1, h2, h3 {
    color: #1f77b4;
}
.block-container {
    max-width: 900px;
    margin: auto;
}
.upload-box, .qa-box {
    background-color: #f9f9fb;
    border: 2px solid #e0e0e0;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
}
.answer-box {
    background-color: #1b282d;
    padding: 1.5rem;
    border-left: 6px solid #1f77b4;
    border-radius: 8px;
    margin-top: 1rem;
}
.source-box {
    background-color: #f6f6f6;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #1f77b4;
    margin-top: 0.5rem;
}
.footer {
    text-align: center;
    color: #999;
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)

if 'uploaded_docs' not in st.session_state:
    st.session_state.uploaded_docs = []
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

st.title("📚 RAG PDF Q&A")
st.caption("Upload a PDF and ask questions powered by **Google Gemini 2.5 Flash**")

def check_backend_health():
    try:
        health = requests.get(HEALTH_URL, timeout=10)
        if health.status_code == 200:
            return True, health.json()
        else:
            return False, {}
    except Exception:
        return False, {}

is_alive, health_status = check_backend_health()

if is_alive:
    st.success("✅ Backend Connected")
    st.caption(f"Vector Store: {health_status.get('vector_store_status', 'OK')}")
else:
    st.error("⚠️ Could not connect to the API backend.")
    if st.button("🔄 Reload"):
        st.rerun()
    st.stop()

tab1, tab2 = st.tabs(["📤 Upload PDF", "💬 Q&A"])

with tab1:
    st.markdown("### Upload and Index a PDF Document")
    with st.form("upload_form"):
        uploaded_file = st.file_uploader(
            "Choose a PDF to upload and index",
            type=["pdf"],
            help="Upload a document to be indexed in the vector database",
        )
        submit_btn = st.form_submit_button("Upload & Index")

        if submit_btn:
            if not uploaded_file:
                st.warning("Please upload a PDF first.")
            else:
                with st.spinner("Processing PDF and creating embeddings..."):
                    try:
                        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
                        resp = requests.post(UPLOAD_URL, files=files, timeout=60)
                        if resp.status_code == 200:
                            data = resp.json()
                            st.success("✅ Uploaded & Indexed Successfully!")
                            st.markdown(f"""
                                **Filename:** {data['filename']}  
                                **Chunks Created:** {data['chunks_created']}  
                                **Collection:** {data['collection_name']}
                            """)
                            st.session_state.uploaded_docs.append(data['filename'])
                        else:
                            st.error(f"Upload failed: {resp.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"🚨 Connection Error: {e}")

with tab2:
    if not st.session_state.uploaded_docs:
        st.warning("Please upload a PDF first in the **Upload PDF** tab.")
    else:
        st.markdown("### Ask Questions About Your Document")
        question = st.text_area(
            "Enter your question:",
            placeholder="Example: What is the main idea of this document?",
            height=120
        )
        top_k = st.slider("Number of sources to retrieve", 1, 10, 3)
        ask_btn = st.button("🤖 Ask Gemini", use_container_width=True)
        show_sources = st.checkbox("Show sources", value=True)

        if ask_btn:
            if not question.strip():
                st.warning("⚠️ Please enter a question.")
            else:
                with st.spinner("Generating answer..."):
                    try:
                        payload = {"question": question, "top_k": top_k}
                        resp = requests.post(QUERY_URL, json=payload, timeout=60)
                        if resp.status_code == 200:
                            data = resp.json()
                            answer = data.get("answer", "No answer generated.")
                            st.markdown("#### 💡 Gemini’s Answer")
                            st.markdown(f"<div class='answer-box'>{answer}</div>", unsafe_allow_html=True)

                            if show_sources and data.get("sources"):
                                st.markdown("#### 📑 Sources")
                                for idx, src in enumerate(data["sources"], 1):
                                    with st.expander(f"Source {idx}: {src['metadata'].get('filename', 'Unknown')}"):
                                        st.write(src["content"])
                                        st.caption(f"Metadata: {src['metadata']}")
                            
                            st.caption(f"🤖 Model Used: {data.get('model_used', 'Gemini 2.5 Flash')}")
                            st.session_state.query_history.append({
                                "question": question,
                                "answer": answer,
                                "time": time.strftime('%Y-%m-%d %H:%M:%S')
                            })
                        else:
                            st.error(f"Query failed: {resp.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"🚨 Connection Error: {e}")

    if st.session_state.query_history:
        st.markdown("---")
        st.markdown("### 📜 Recent Queries")
        for q in reversed(st.session_state.query_history[-3:]):
            with st.expander(f"Q: {q['question'][:80]}..."):
                st.markdown(f"**Time:** {q['time']}")
                st.markdown(f"**Answer:** {q['answer']}")
