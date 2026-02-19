import streamlit as st
from utils.llm import ask_llm
from pypdf import PdfReader

def rag_ui():
    st.header("📄 Document Chat")

    pdf = st.file_uploader("Upload PDF")

    if pdf:
        reader = PdfReader(pdf)
        text = ""

        for page in reader.pages:
            text += page.extract_text()

        text = text[:4000]  # Prevent token overflow

        question = st.text_input("Ask question")

        if st.button("Ask"):
            prompt = f"Answer from document:\n{text}\nQuestion:{question}"
            st.write(ask_llm(prompt))
