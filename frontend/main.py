import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(page_title="Gemini Q&A", page_icon="💬", layout="centered")

st.title("🤖 Gemini Q&A Chat")
st.write("Ask anything, and get answers from Google Gemini!")

question = st.text_area("💭 Enter your question here:", height=100)

if st.button("Ask Gemini"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json={"question": question})
                if response.status_code == 200:
                    data = response.json()
                    if "answer" in data:
                        st.success("### 💡 Gemini's Response")
                        st.markdown(data["answer"])
                    else:
                        st.error(f"❌ Error: {data.get('error', 'Unknown error')}")
                else:
                    st.error(f"⚠️ API Error: {response.status_code}")
            except Exception as e:
                st.error(f"🚨 Connection Error: {e}")
