import streamlit as st
from utils.llm import ask_llm

def chatbot_ui():
    st.header("💬 Chatbot")

    text = st.text_input("Ask anything")

    if st.button("Send"):
        st.write(ask_llm(text))
