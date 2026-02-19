🎯 Purpose of This Project
This project was designed to simulate a real-world Generative AI system by combining multiple AI capabilities into one production-ready assistant. It demonstrates how LLMs can be integrated with multimodal inputs, memory optimization, and secure cloud deployment to build scalable AI applications.

🤖 Multimodal GenAI Assistant

A ChatGPT-style **Multimodal Generative AI Assistant** built using Streamlit and Gemini LLM.  
This project integrates conversational AI, document-based Q&A, and YouTube video summarization into a single intelligent interface with memory optimization and secure API deployment.

🌟 Project Overview

Multimodal GenAI Assistant is designed to simulate a real-world AI product architecture.  
It supports multiple input types such as text, voice, PDF documents, and video links while maintaining conversational memory and optimized token usage.

Unlike traditional chatbots, this system combines multiple AI workflows into a unified LLM-driven pipeline.

⭐ Key Features

💬 ChatGPT-style conversational interface
📄 Document Chat (RAG-style PDF Q&A)
🎥 YouTube Video Summarization
🎤 Voice Input & Text-to-Speech
🧠 Memory Optimization with Summary Storage
🔒 Secure API Key Handling (Streamlit Secrets)
🎨 Custom AI Interface (Not default Streamlit UI)



 🚀 What Makes This Project Unique

✔ Centralized LLM Brain controlling multiple AI tools  
✔ Multimodal interaction (text + voice + document + video)  
✔ Token-efficient summarized memory system  
✔ Production-style modular architecture  
✔ Secure deployment without exposing API keys  

Most beginner projects only implement chat — this system demonstrates **real GenAI engineering workflows**.

---

## 🧠 Architecture Overview

                ┌─────────────────────┐
                │       User Input     │
                │ Text / Voice / PDF   │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Streamlit UI       │
                │ ChatGPT-style Input  │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Chat Controller    │
                │ (modules/chatbot)    │
                └──────────┬──────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   Document Mode      Video Mode        Chat Mode
     (PDF RAG)        (Transcript)       (Memory)

                           │
                           ▼
                ┌─────────────────────┐
                │   utils/llm.py       │
                │  Gemini API Brain    │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Gemini LLM API     │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  Response to UI      │
                └─────────────────────┘


GenAI-Assistant/
│
├── app.py
├── requirements.txt
│
├── modules/
│ └── chatbot.py
│
└── utils/
├── llm.py
└── summary_memory.py


deployment: https://multigenai.streamlit.app/
