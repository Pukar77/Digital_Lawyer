import streamlit as st
import google.generativeai as genai
from src.vector_store import QdrantHandler
from dotenv import load_dotenv
import os

# --- INITIALIZATION ---
load_dotenv() 

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    st.error("GEMINI_API_KEY not found in .env file. Please check your setup.")
else:
    # Setup Google Gemini Model
    genai.configure(api_key=GOOGLE_API_KEY)
    @st.cache_resource
    def get_model():
        
        return genai.GenerativeModel('gemini-2.5-flash')
    
    model = get_model()

    # Initialize Database Connection (cached to prevent reconnecting on every rerun)
    @st.cache_resource
    def get_qdrant_handler():
        return QdrantHandler()
    
    db = get_qdrant_handler()


# --- PAGE SETUP ---
st.set_page_config(page_title="Nepal Legal Advisor AI", page_icon="⚖️")
st.title("🇳🇵 Nepal Constitution AI Advisor")
st.markdown("Ask a question about your rights or the law, and I will reference the relevant Articles.")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT LOGIC ---
if user_input := st.chat_input("E.g., What are my fundamental rights regarding free speech?"):
    
    # 1. Display User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Retrieve Relevant Laws (RAG)
    with st.spinner("Searching Constitution..."):
        # Retrieve top 3 most relevant chunks from Qdrant
        search_results = db.search(user_input, top_k=3)
        
        # Format retrieved laws into a clean context string for the LLM
        context_text = ""
        for i, result in enumerate(search_results):
            payload = result.payload
            context_text += f"--- Source {i+1} (Score: {result.score:.2f}) ---\n"
            context_text += f"Part: {payload['part_number']}, Article: {payload['article_number']}\n"
            context_text += f"Content: {payload['text']}\n\n"

    # 3. Construct Prompt with Context
    prompt = f"""
    You are an expert Legal Advisor for Nepal. Your task is to answer the user's question 
    based **STRICTLY** on the constitutional text provided below as context. 
    
    **Instructions:**
    1. Quote the specific **Part** and **Article** numbers when referencing the law.
    2. Provide a clear, polite, and comprehensive answer.
    3. If the context does not contain the answer, state that you cannot find the information in the Constitution of Nepal.
    
    ---
    **CONTEXT:**
    {context_text}
    ---
    
    **USER QUESTION:** {user_input}
    
    **ADVICE:**
    """
    
    # 4. Generate Response using Gemini
    with st.spinner("Generating legal advice..."):
        try:
            response = model.generate_content(prompt)
            ai_reply = response.text
        except Exception as e:
            ai_reply = f"Error: Could not connect to Gemini API. Check your API key or network connection. Details: {e}"

    # 5. Display AI Response
    with st.chat_message("assistant"):
        st.markdown(ai_reply)
    
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})



