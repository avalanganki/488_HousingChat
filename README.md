# 🏠 Syracuse University Housing Assistant

A retrieval-augmented generation (RAG) chatbot that answers questions about Syracuse University residence halls — room types, dining options, and other housing details — using official SU housing data.

Live app: housingchat488.streamlit.app

Features
- Natural language Q&A over official SU housing data (residence halls, room types, dining, etc.)
- Adjustable retrieval depth — controls how much context the assistant reviews before answering (tradeoff between speed and thoroughness)
- Reranking toggle — reorders retrieved documents by relevance before passing them to the LLM, improving answer accuracy
Streamlit UI for a clean, interactive chat experience

How it works
- SU housing data is embedded and stored in a vector database
- On a user query, relevant chunks are retrieved (depth configurable via the sidebar)
- Optional reranking step reorders results by relevance
- Retrieved context + query are passed to the OpenAI API to generate a grounded answer

Tech stack
- Frontend: Streamlit
- LLM: OpenAI API
- Retrieval: Vector database (e.g., FAISS/Chroma/Pinecone)
- Language: Python

Running locally
bash
git clone https://github.com/avalanganki/488_HousingChat.git
cd 488_HousingChat
pip install -r requirements.txt
streamlit run app.py

You'll need an OpenAI API key set as an environment variable (OPENAI_API_KEY).

Project context
- Built for IST 488: AI Chatbots at Syracuse University's iSchool.
