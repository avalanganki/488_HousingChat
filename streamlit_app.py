__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
 
import streamlit as st
from openai import OpenAI
import chromadb
 
 
# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="SU Housing Assistant",
    page_icon="🏠",
    layout="centered"
)
 
st.title("🏠 Syracuse University Housing Assistant")
st.caption("Ask me anything about SU residence halls, room types, dining, and more.")
 
 
# ============================================================
# LOAD CHROMADB (cached so it only runs once per session)
# ============================================================
@st.cache_resource
def load_chroma():
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection("su_housing")
    return collection
 
collection = load_chroma()
 
 
# ============================================================
# OPENAI CLIENT
# ============================================================
# Uses Streamlit secrets — set OPENAI_API_KEY in .streamlit/secrets.toml
# or in Streamlit Cloud app settings > Secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
 
 
# ============================================================
# SYSTEM PROMPT
# ============================================================
SYSTEM_PROMPT = """You are the Syracuse University Housing Assistant, a helpful chatbot 
that answers questions about SU residence halls and housing options.
 
RULES:
- Only answer questions using the provided housing context below. 
- If the context does not contain enough information to answer, say so honestly.
- Do NOT make up information or use general knowledge about Syracuse University.
- Be conversational and friendly — like a knowledgeable upperclassman helping out.
- When comparing halls, organize your answer clearly.
- If a student mentions their class year, use that to filter your recommendations 
  (e.g., freshmen can't live in Booth Hall).
 
HOUSING CONTEXT:
{context}
"""
 
 
# ============================================================
# RAG QUERY FUNCTION
# ============================================================
def get_housing_context(user_question, n_results=3):
    """
    Query ChromaDB for the most relevant housing data chunks.
    Returns the concatenated text of the top results.
    """
    results = collection.query(
        query_texts=[user_question],
        n_results=n_results,
    )
    
    # Combine the retrieved documents into one context string
    context_pieces = results["documents"][0]  # list of strings
    return "\n\n---\n\n".join(context_pieces)
 
 
# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.header("About")
    st.write(
        "This chatbot uses official Syracuse University housing data "
        "to answer your questions about residence halls."
    )
    
    # Optional: let user control retrieval depth
    n_results = st.slider(
        "Number of data chunks to retrieve",
        min_value=1,
        max_value=7,
        value=3,
        help="Higher = more context for the LLM, but slower and more tokens used."
    )
    
    # TODO (Person 3 — Polish): Add class year filter
    # class_year = st.selectbox("I am a...", ["Anyone", "Freshman", "Sophomore", "Transfer"])
 
 
# ============================================================
# CHAT HISTORY (session state)
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
 
# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
 
 
# ============================================================
# CHAT INPUT & RESPONSE
# ============================================================
if user_input := st.chat_input("Ask about SU housing..."):
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # --- RAG Pipeline ---
    # Step 1: Retrieve relevant housing data from ChromaDB
    context = get_housing_context(user_input, n_results=n_results)
    
    # Step 2: Build the prompt with retrieved context
    system_with_context = SYSTEM_PROMPT.format(context=context)
    
    # Step 3: Build message history for OpenAI
    # Include system prompt + conversation history + new message
    openai_messages = [{"role": "system", "content": system_with_context}]
    
    # Add conversation history (so the bot can handle follow-ups)
    for msg in st.session_state.messages:
        openai_messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Step 4: Call OpenAI with streaming
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=openai_messages,
            temperature=0.3,  # Low temp for factual accuracy
            stream=True,
        )
        response = st.write_stream(stream)
    
    # Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response})
