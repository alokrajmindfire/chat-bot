"""
Streamlit UI for RAG Pipeline
Upload PDFs and Query with Gemini
"""

import streamlit as st
import requests
from typing import Optional
import time

API_BASE_URL = "http://127.0.0.1:8000"
UPLOAD_URL = f"{API_BASE_URL}/documents/upload"
QUERY_URL = f"{API_BASE_URL}/query/"
HEALTH_URL = f"{API_BASE_URL}/health"

st.set_page_config(
    page_title="RAG Pipeline - PDF Q&A",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .query-section {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
    .source-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
        margin-top: 1rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border-radius: 5px;
        color: #155724;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

if 'upload_history' not in st.session_state:
    st.session_state.upload_history = []
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

st.markdown('<div class="main-header">📚 RAG Pipeline - PDF Q&A</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload PDFs and ask questions powered by Google Gemini 2.5 Flash</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Health Check
    try:
        health_response = requests.get(HEALTH_URL, timeout=2)
        if health_response == 200:
            health_data = health_response.json()
            st.success("✅ API Connected")
            st.caption(f"Vector Store: {health_data.get('vector_store_status', 'Unknown')}")
        else:
            st.error("❌ API Not Responding")
    except:
        st.error("❌ API Connection Failed")
        st.caption(f"Make sure the API is running at {API_BASE_URL}")
    
    st.divider()
    
    # Query Settings
    st.subheader("Query Settings")
    top_k = st.slider("Number of sources to retrieve", min_value=1, max_value=10, value=3)
    
    st.divider()
    
    # Upload History
    st.subheader("📁 Upload History")
    if st.session_state.upload_history:
        for idx, upload in enumerate(reversed(st.session_state.upload_history[-5:])):
            st.caption(f"✓ {upload['filename']}")
            st.caption(f"   {upload['chunks']} chunks")
    else:
        st.caption("No uploads yet")
    
    st.divider()
    
    # Clear History
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.query_history = []
        st.session_state.upload_history = []
        st.rerun()

# Main Content
col1, col2 = st.columns([1, 1])

# Left Column - Upload Section
with col1:
    st.markdown("## 📤 Upload PDF")
    
    with st.container():
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a PDF document to index in the vector database"
        )
        
        if uploaded_file is not None:
            st.info(f"📄 **File:** {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("🚀 Upload & Index", type="primary", use_container_width=True):
                    with st.spinner("Processing PDF and creating embeddings..."):
                        try:
                            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
                            response = requests.post(UPLOAD_URL, files=files)
                            
                            if response.status_code == 200:
                                data = response.json()
                                st.success("✅ PDF uploaded and indexed successfully!")
                                
                                # Display upload details
                                st.markdown(f"""
                                <div class="success-message">
                                    <strong>Upload Details:</strong><br>
                                    📄 Filename: {data['filename']}<br>
                                    📊 Chunks Created: {data['chunks_created']}<br>
                                    🗂️ Collection: {data['collection_name']}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Add to history
                                st.session_state.upload_history.append({
                                    'filename': data['filename'],
                                    'chunks': data['chunks_created'],
                                    'time': time.strftime('%Y-%m-%d %H:%M:%S')
                                })
                                
                            else:
                                st.error(f"❌ Upload failed: {response.json().get('detail', 'Unknown error')}")
                        
                        except Exception as e:
                            st.error(f"🚨 Connection Error: {e}")
            
            with col_btn2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.rerun()

# Right Column - Query Section
with col2:
    st.markdown("## 💬 Ask Questions")
    
    with st.container():
        question = st.text_area(
            "💭 Enter your question here:",
            height=150,
            placeholder="What is the main topic discussed in the document?",
            help="Ask anything about the uploaded PDFs"
        )
        
        col_btn3, col_btn4 = st.columns([3, 1])
        
        with col_btn3:
            ask_button = st.button("🤖 Ask Gemini", type="primary", use_container_width=True)
        
        with col_btn4:
            show_sources = st.checkbox("Show sources", value=True)
        
        if ask_button:
            if not question.strip():
                st.warning("⚠️ Please enter a question.")
            else:
                with st.spinner("🔍 Searching documents and generating answer..."):
                    try:
                        payload = {
                            "question": question,
                            "top_k": top_k
                        }
                        response = requests.post(QUERY_URL, json=payload)
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Display Answer
                            st.markdown("### 💡 Gemini's Answer")
                            st.markdown(f"""
                            <div style="background-color: #1b282d; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #1f77b4;">
                                {data['answer']}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Display Sources
                            if show_sources and data.get('sources'):
                                st.markdown("### 📑 Sources")
                                
                                for idx, source in enumerate(data['sources'], 1):
                                    with st.expander(f"📄 Source {idx} - {source['metadata'].get('filename', 'Unknown')}"):
                                        st.markdown(f"**Content:**")
                                        st.text(source['content'])
                                        
                                        st.markdown("**Metadata:**")
                                        for key, value in source['metadata'].items():
                                            st.caption(f"• {key}: {value}")
                            
                            # Model Info
                            st.caption(f"🤖 Model: {data.get('model_used', 'Unknown')}")
                            
                            # Add to history
                            st.session_state.query_history.append({
                                'question': question,
                                'answer': data['answer'][:200] + '...',
                                'time': time.strftime('%Y-%m-%d %H:%M:%S')
                            })
                            
                        else:
                            st.error(f"❌ Query failed: {response.json().get('detail', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"🚨 Connection Error: {e}")

# Query History Section
if st.session_state.query_history:
    st.markdown("---")
    st.markdown("## 📜 Recent Queries")
    
    for idx, query in enumerate(reversed(st.session_state.query_history[-3:])):
        with st.expander(f"Q: {query['question'][:80]}..." if len(query['question']) > 80 else f"Q: {query['question']}"):
            st.markdown(f"**Time:** {query['time']}")
            st.markdown(f"**Answer:** {query['answer']}")