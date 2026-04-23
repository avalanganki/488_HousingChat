# Imports
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
 
import streamlit as st
from openai import OpenAI
import chromadb
import json
import os
import requests
 
# Page Configurations
st.set_page_config(
    page_title="SU Housing Assistant",
    page_icon="🏠",
    layout="centered"
)
 
st.markdown("<h1 style='color: #F76900;'>🏠 Syracuse University Housing Assistant</h1>", unsafe_allow_html=True)
st.caption("Ask anything about SU residence halls, room types, dining, and more.")
 
 
# Loading ChromaDB - cached
@st.cache_resource
def load_chroma():
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection("su_housing")
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
- "neighborhood_preference": north neighborhood, west neighborhood, east neighborhood, south campus.
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
        "neighborhood_preference": "Neighborhood Preference",
        "amenities_preference": "Amenities Preferences",
        "hall_preference": "Hall Preference",
        "other_preferences": "Other Preferences",
    }
    for key, value in memory.items():
        label = labels.get(key, key)
        lines.append(f"- {label}: {value}")
    return "\n".join(lines)


# Reranking using nano
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
 
 
def get_housing_context(user_question, n_results=3, use_reranking=True):
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
        best_chunks = [chunk for _, chunk in scored[:n_results]]
    else:
        # No reranking — original behavior
        results = collection.query(
            query_texts=[user_question],
            n_results=n_results,
        )
        best_chunks = results["documents"][0]
 
    return "\n\n---\n\n".join(best_chunks)


# WALKING TOOL CODE HERE
# Walking Distance Tool
def get_walking_distance(origin, destination):
    """
    Uses Google Maps Routes API to get walking distance and time
    between two locations on/near Syracuse University campus.
    """
    api_key = st.secrets["GOOGLE_MAPS_API_KEY"]
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.legs.duration,routes.legs.distanceMeters"
    }
    
    body = {
        "origin": {
            "address": f"{origin}, Syracuse University, Syracuse, NY"
        },
        "destination": {
            "address": f"{destination}, Syracuse University, Syracuse, NY"
        },
        "travelMode": "WALK"
    }
    
    try:
        response = requests.post(url, headers=headers, json=body)
        data = response.json()
        
        if "routes" in data and len(data["routes"]) > 0:
            route = data["routes"][0]
            distance_meters = route["distanceMeters"]
            duration_seconds = int(route["duration"].replace("s", ""))
            
            distance_miles = round(distance_meters * 0.000621371, 2)
            duration_minutes = (duration_seconds / 60)
            
            return f"Walking from {origin} to {destination}: approximately {distance_miles} miles ({duration_minutes} minutes on foot)."
        else:
            return f"Sorry, I couldn't find walking directions from {origin} to {destination}."
    except Exception as e:
        return f"Error getting walking directions: {str(e)}"


# System Prompt
SYSTEM_PROMPT = """You are the Syracuse University Housing Assistant, a helpful chatbot 
that answers questions about SU residence halls and housing options.
 
RULES:
- Only answer questions using the provided housing context below. 
- If the context does not contain enough information to answer, say so honestly. Do not pull from other data. 
- Do NOT make up information or use general knowledge about Syracuse University.
- Be conversational and friendly — like a knowledgeable upperclassman helping out.
- When comparing halls, organize your answer clearly.
- If a student mentions their class year, use that to filter your recommendations 
  (e.g., freshmen can't live in Booth Hall).
- The student's class year from the sidebar filter is: {class_year}. 
  If it's "Not specified", ask them if relevant. If specified, ALWAYS filter your 
  recommendations based on housing eligibility for that class year.
- If you know the student's preferences (listed below), use them to personalize your answers.

STUDENT PREFERENCES (from previous conversations):
{preferences}

WALKING DIRECTIONS:
If a student asks about walking distance, how far something is, or how long it takes 
to walk between two locations, you will be given walking distance data. Use it in your answer.

{walking_info}
 
HOUSING CONTEXT:
{context}
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
 
    # Check if user is asking about walking distance
    walking_info = ""
    walking_keywords = ["walk", "distance", "how far", "minutes from", "close to", "near", "get to", "commute"]
    if any(keyword in user_input.lower() for keyword in walking_keywords):
        # Use GPT to extract the two locations from the question
        extract_prompt = f"""The user is asking about walking distance between locations at Syracuse University.
Extract the two locations from their question. Return ONLY a JSON object like:
{{"origin": "location 1", "destination": "location 2"}}

If you can't find two clear locations, return: {{"error": "true"}}

USER QUESTION: {user_input}"""
        
        try:
            extract_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": extract_prompt}],
                temperature=0,
                max_tokens=100,
            )
            result = extract_response.choices[0].message.content.strip()
            result = result.replace("```json", "").replace("```", "").strip()
            locations = json.loads(result)
            
            if "error" not in locations:
                walking_info = get_walking_distance(locations["origin"], locations["destination"])
        except (json.JSONDecodeError, Exception):
            pass

    # Step 1 & 2: Retrieve + optionally rerank
    context = get_housing_context(user_input, n_results=n_results, use_reranking=use_reranking)

    # Step 3: Build system prompt with context AND memory
    system_with_context = SYSTEM_PROMPT.format(
        context=context,
        preferences=format_memory_for_prompt(memory),
        class_year=class_year,
        walking_info=walking_info if walking_info else "No walking directions requested.",
    )

    # Step 4 & 5: Call Responses API with streaming
    with st.chat_message("assistant"):
        stream = client.responses.create(
            model="gpt-4o",
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