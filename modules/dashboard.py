import streamlit as st

def dashboard_ui():
    st.header("🧠 AI Studio Dashboard")

    if "history" in st.session_state:
        st.write(f"Messages stored: {len(st.session_state.history)}")
    else:
        st.write("No chat history yet.")

    st.write("Model: Gemini Flash")
    st.write("Modules:")
    st.write("✔ RAG")
    st.write("✔ Video Summarizer")
    st.write("✔ Image Generator")
    st.write("✔ Chatbot")
