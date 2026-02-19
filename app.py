import streamlit as st
from modules.chatbot import chatbot_ui

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="GenAI Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- SESSION STATE ----------
if "show_history" not in st.session_state:
    st.session_state.show_history = False

# ---------- CSS ----------
st.markdown("""
<style>
.stChatInputContainer {
    position:relative;
}

.plus-inside {
    position:absolute;
    left:18px;
    bottom:14px;
    font-size:20px;
    pointer-events:none;
}

.mic-inside {
    position:absolute;
    right:60px;
    bottom:14px;
    font-size:18px;
    pointer-events:none;
}



textarea {
    padding-left:40px !important;
}


</style>
""", unsafe_allow_html=True)

# ---------- TOP BAR ----------
col1, col2 = st.columns([1,10])

with col1:
    if st.button("☰"):
        st.session_state.show_history = not st.session_state.show_history

with col2:
    st.markdown("### GenAI Assistant")

# ---------- HISTORY PANEL ----------
if st.session_state.show_history:

    st.markdown('<div class="history-panel">', unsafe_allow_html=True)
    st.markdown("#### 🕘 History")

    if "messages" in st.session_state:
        for m in st.session_state.messages:
            st.write(f"**{m['role']}**: {m['content']}")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- HERO TEXT ----------
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.markdown('<div class="hero"></div>', unsafe_allow_html=True)

# ---------- LOAD CHATBOT ----------
chatbot_ui()
