# Imports
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
 
import streamlit as st
from openai import OpenAI
import chromadb
import json
import os
 
# Page Configurations
st.set_page_config(
    page_title="SU Housing Assistant",
    page_icon="🏠",
    layout="centered"
)
 
st.markdown("<h1 style='color: #F76900;'>🏠 Syracuse University Housing Assistant</h1>", unsafe_allow_html=True)
st.caption("Ask anything about SU residence halls, room types, dining, and more.")
 
 
@st.cache_resource
def load_chroma():
    from build_db import housing_chunks
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="su_housing")
    if collection.count() == 0:
        ids = [c["id"] for c in housing_chunks]
        documents = [c["text"] for c in housing_chunks]
        metadatas = [c["metadata"] for c in housing_chunks]
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return collection

collection = load_chroma()
 
# OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# Long-Term Memory: JSON Approach
LTM_FILE = "user_memory.json"
 
def load_memory():
    """Load user preferences from JSON file."""
    if os.path.exists(LTM_FILE):
        with open(LTM_FILE, "r") as f:
            return json.load(f)
    return {}
 
def save_memory(memory):
    """Save user preferences to JSON file."""
    with open(LTM_FILE, "w") as f:
        json.dump(memory, f, indent=2)
 
def extract_preferences(user_message, assistant_response, current_memory):
    """
    Use GPT-4o-mini to extract user preferences from the conversation.
    Only runs when the conversation might contain preference info.
    """
    extraction_prompt = f"""Analyze this conversation exchange and extract any user preferences 
related to Syracuse University housing. Return ONLY a valid JSON object with any of these keys 
(only include keys where info is clearly stated):
 
- "class_year": freshman, sophomore, junior, senior, transfer, graduate
- "room_type": single, double, triple, suite, apartment
- "budget": any mention of budget or price preference
- "location_preference": quiet, social, near dining, near campus center, etc.
- "amenities_preference": laundry wants, fitness centers, study rooms, kitchen types, air conditioning, penthouse access, music room access, computer clusters, entertainment areas.
- "hall_preference": any specific halls they like or dislike
- "other_preferences": any other housing preference mentioned
 
If NO preferences are found, return exactly: {{"no_preferences": true}}
 
USER MESSAGE: {user_message}
ASSISTANT RESPONSE: {assistant_response}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0,
            max_tokens=300,
        )
        result = response.choices[0].message.content.strip()
        result = result.replace("```json", "").replace("```", "").strip()
        new_prefs = json.loads(result)
 
        if "no_preferences" not in new_prefs:
            current_memory.update(new_prefs)
            save_memory(current_memory)
            return current_memory
    except (json.JSONDecodeError, Exception):
        pass  # If extraction fails, skip
 
    return current_memory
 
def format_memory_for_prompt(memory):
    """Format stored preferences into a string for the system prompt."""
    if not memory:
        return "No known preferences yet."
    
    lines = []
    labels = {
        "class_year": "Class Year",
        "room_type": "Preferred Room Type",
        "budget": "Budget",
        "location_preference": "Location Preference",
        "amenities_preference": "Amenities Preferences",
        "hall_preference": "Hall Preference",
        "other_preferences": "Other Preferences",
    }
    for key, value in memory.items():
        label = labels.get(key, key)
        lines.append(f"- {label}: {value}")
    return "\n".join(lines)


# Reranking using GPT-4o-mini
def score_chunk(chunk, question):
    """Score how relevant a chunk is to the user's question (1-10)."""
    scoring_prompt = f"""Rate how relevant this text is to answering the question.
Respond with ONLY a number from 1 to 10. Nothing else.
 
QUESTION: {question}
 
TEXT: {chunk}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": scoring_prompt}],
            temperature=0,
            max_tokens=5,
        )
        score = int(response.choices[0].message.content.strip())
        return min(max(score, 1), 10)
    except (ValueError, Exception):
        return 5 
 
 
def get_walking_context(user_question, collection):
    """
    If the user is asking a walking/distance/proximity question, retrieve ALL
    walking distance chunks so the LLM has complete data. Returns them as a
    separate string (or empty string if not a walking question).
    """
    walking_keywords = ["walk", "distance", "how far", "minutes from", "close to",
                        "near", "closest", "get to", "commute", "proximity"]
    if not any(kw in user_question.lower() for kw in walking_keywords):
        return ""

    # Pull all walking distance chunks by metadata
    results = collection.get(
        where={"hall": "Walking Distances"},
        include=["documents"],
    )
    if results and results["documents"]:
        return "\n\n---\n\n".join(results["documents"])
    return ""


def get_housing_context(user_question, collection, n_results=3, use_reranking=True):
    """
    Query ChromaDB for relevant housing data.
    If reranking is on: over-retrieve, score each chunk, keep the best ones.
    """
    if use_reranking:
        # Step 1: Over-retrieve (get 3x what we need)
        over_fetch = min(n_results * 3, 10)
        results = collection.query(
            query_texts=[user_question],
            n_results=over_fetch,
        )
        candidates = results["documents"][0]
 
        # Step 2: Score each chunk
        scored = []
        for chunk in candidates:
            score = score_chunk(chunk, user_question)
            scored.append((score, chunk))
 
        # Step 3: Sort by score (highest first) and keep top n_results
        scored.sort(key=lambda x: x[0], reverse=True)
        best_chunks = [chunk for score, chunk in scored if score >= 5]
        if len(best_chunks) == 0:
            best_chunks = [chunk for _, chunk in scored[:n_results]]
        elif len(best_chunks) > n_results:
            best_chunks = best_chunks[:n_results]
    else:
        # No reranking — original behavior
        results = collection.query(
            query_texts=[user_question],
            n_results=n_results,
        )
        best_chunks = results["documents"][0]
 
    return "\n\n---\n\n".join(best_chunks)


# System Prompt
SYSTEM_PROMPT = """You are the Syracuse University Housing Assistant, a helpful chatbot 
that answers questions about SU residence halls and housing options.

RULES:
- ONLY use the HOUSING CONTEXT provided below to answer questions. 
- If the answer is NOT explicitly stated in the HOUSING CONTEXT, say: 
  "I don't have that information in my housing database. I'd recommend checking 
  the Syracuse University Housing website or contacting the Office of Residence Life."
- Do NOT use any outside knowledge about Syracuse University, even if you believe it to be true.
- Do NOT guess, infer, or fill in gaps. If the context is incomplete, say so.
- Be conversational and friendly — like a knowledgeable upperclassman helping out.
- When comparing halls, organize your answer clearly.
- If a student mentions their class year, use that to filter your recommendations 
  (e.g., freshmen can't live in Booth Hall).
- The student's class year from the sidebar filter is: {class_year}. 
  If it's "Not specified", ask them if relevant. If specified, ALWAYS filter your 
  recommendations based on housing eligibility for that class year.
- If you know the student's preferences (listed below), use them to personalize your answers.

WALKING DISTANCES:
- The housing context includes pre-computed walking distances from major campus landmarks 
  (Whitman, Bird Library, Schine, the Dome, the Quad, Life Sciences) to every residence hall.
- When a student asks how far a hall is from a building, or which halls are closest to a 
  landmark, use the walking distance data from the context to answer.
- Always include the approximate miles AND minutes when citing walking distances.
- For South Campus locations (Skyhall I/II/III, South Campus Apartments), note that a 
  shuttle is required to get to main campus.

STUDENT PREFERENCES (from previous conversations):
{preferences}

HOUSING CONTEXT:
{context}

REMINDER: If the HOUSING CONTEXT above does not contain the answer, do NOT make one up. 
Say you don't have that information and direct the student to official SU Housing resources.
"""
 
 
# Sidebar
st.markdown(
    """
    <style>
    /* Slider track and thumb */
    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #F76900 !important;
    }
    .stSlider > div > div > div > div {
        background-color: #F76900 !important;
    }

    /* Toggle when active */
    .stToggle > label > div[data-testid="toggle"] > div {
        background-color: #F76900 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("About")
    st.write(
        "This chatbot uses official Syracuse University housing data "
        "to answer your questions about residence halls."
    )

    # Retrieval depth
    n_results = st.slider(
        "Retrieval Depth",
        min_value=1,
        max_value=7,
        value=3,
    )
    st.caption("Higher means the assistant reviews more information before answering, but may take longer.")    

    # Reranking toggle
    use_reranking = st.toggle(
        "Enable reranking",
        value=True,
        help="Uses AI to pick the most relevant chunks. More accurate but slightly slower.",
    )

    st.divider()

    # Class year filter
    st.header("Your Info")
    class_year = st.selectbox(
        "I am a...",
        ["Not specified", "Freshman", "Sophomore", "Junior", "Senior", "Transfer", "Graduate"],
        help="This helps filter housing recommendations to what you're eligible for.",
    )
    # Save class year to LTM when selected
    if class_year != "Not specified":
        memory = load_memory()
        if memory.get("class_year") != class_year.lower():
            memory["class_year"] = class_year.lower()
            save_memory(memory)

    st.divider()

    # Show stored preferences
    st.header("Your Preferences")
    memory = load_memory()
    if memory:
        for key, value in memory.items():
            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        if st.button("Clear My Preferences"):
            save_memory({})
            st.rerun()
    else:
        st.write("No preferences saved yet. Just chat and I'll learn what matters to you!")
 

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_response_id" not in st.session_state:
    st.session_state.last_response_id = None
 
# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
 
 
# Input and Response 
if user_input := st.chat_input("Ask about SU housing..."):
 
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
 
    # Load current memory
    memory = load_memory()
 
    # Step 1: Check if this is a walking/distance question — if so, grab ALL distance chunks
    walking_context = get_walking_context(user_input, collection)

    # Step 2: Retrieve hall info from ChromaDB via normal RAG pipeline
    housing_context = get_housing_context(user_input, collection, n_results=n_results, use_reranking=use_reranking)

    # Step 3: Combine — walking distances go first so the LLM always has full data
    if walking_context:
        context = walking_context + "\n\n---\n\n" + housing_context
    else:
        context = housing_context

    # Build system prompt with context AND memory
    system_with_context = SYSTEM_PROMPT.format(
        context=context,
        preferences=format_memory_for_prompt(memory),
        class_year=class_year,
    )

    # Call Responses API with streaming
    with st.chat_message("assistant"):
        stream = client.responses.create(
            model="gpt-4.1",
            instructions=system_with_context,
            input=user_input,
            previous_response_id=st.session_state.last_response_id,
            stream=True,
            temperature=0.3,
        )

        response = ""
        response_id = None
        response_container = st.empty()
        for event in stream:
            if event.type == "response.output_text.delta":
                response += event.delta
                response_container.markdown(response)
            elif event.type == "response.completed":
                response_id = event.response.id

    # Save the response ID for next turn
    if response_id:
        st.session_state.last_response_id = response_id

    # Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response})

    # LTM: Extract preferences in the background
    memory = extract_preferences(user_input, response, memory)