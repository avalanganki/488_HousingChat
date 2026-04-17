import chromadb
import os
 
# ============================================================
# 1. DEFINE YOUR ATTRIBUTE-BASED CHUNKS
# ============================================================
# Each chunk is one attribute across ALL halls.
# This makes comparison queries ("which dorms have pod bathrooms?") 
# hit the right chunk in one retrieval.
 
housing_chunks = [
    {
        "id": "room_types",
        "text": """Attribute: Room Types by Residence Hall
 
Singles are available in: Boland Hall, Booth Hall, Brewster Hall, Brockway Hall, Day Hall, DellPlain Hall, Ernie Davis Hall, Haven Hall, Lawrinson Hall, Oren Lyons Hall, Sadler Hall, Shaw Hall, Watson Hall.
Open doubles are available in: Booth Hall, Brockway Hall, Day Hall, DellPlain Hall, Ernie Davis Hall, Haven Hall, Lawrinson Hall, Oren Lyons Hall, Shaw Hall, Watson Hall, Orange Hall.
Split doubles are available in: Boland Hall, Booth Hall, Brewster Hall, Day Hall, DellPlain Hall, Haven Hall, Shaw Hall.
Two-person suites are available in: Booth Hall, Haven Hall, Washington Arms.
Three-person suites are available in: Oren Lyons Hall, Washington Arms.
Four-person suites are available in: Booth Hall, Brewster Hall, Haven Hall.
Open triples are available in: Oren Lyons Hall, Orange Hall.
Studio and one-, two-, and four-bedroom apartments are available in: 801 University Ave, 727 South Crouse Ave.""",
        "metadata": {"attribute": "room_types"}
    },
    {
        "id": "bathroom_types",
        "text": """Attribute: Bathroom Types by Residence Hall
 
Pod-style private bathrooms (individual lockable rooms with shower, toilet, and sink): Booth Hall, DellPlain Hall, Ernie Davis Hall, Haven Hall, Oren Lyons Hall, Watson Hall.
Communal shared bathrooms (single-gender, shared by the full floor): Boland Hall, Brewster Hall, Brockway Hall, Day Hall, Lawrinson Hall, Sadler Hall, Shaw Hall.
In-room private bathrooms: Orange Hall, 801 University Ave, 727 South Crouse Ave, Washington Arms.""",
        "metadata": {"attribute": "bathroom_types"}
    },
    {
        "id": "dining_access",
        "text": """Attribute: Dining Hall Access by Residence Hall
 
Ernie Davis Dining Center is closest to: Booth Hall, DellPlain Hall, Ernie Davis Hall, Haven Hall, Watson Hall, Walnut Hall.
Sadler Dining Hall is closest to: Boland Hall, Brewster Hall, Brockway Hall, Lawrinson Hall, Sadler Hall.
Shaw Dining Hall is located inside: Shaw Hall.
Goldstein Food Hall (South Campus) is closest to: Skyhall I, Skyhall II, Skyhall III, South Campus apartments.
An unlimited meal plan is required for all students living in North Campus residence halls. South Campus residents may choose a meal plan but are not required to have one.""",
        "metadata": {"attribute": "dining_access"}
    },
    {
        "id": "neighborhoods",
        "text": """Attribute: Neighborhood and Location by Residence Hall
 
North Neighborhood: Booth Hall, Haven Hall, Milton Hall, Orange Hall, Walnut Hall, Washington Arms, 727 South Crouse Ave, 801 University Ave.
West Neighborhood: Boland Hall, Brewster Hall, Brockway Hall, Lawrinson Hall, Sadler Hall.
Central Campus: Day Hall, DellPlain Hall, Ernie Davis Hall, Shaw Hall, Watson Hall.
East Campus: Oren Lyons Hall.
South Campus: Skyhall I, Skyhall II, Skyhall III, South Campus apartments.""",
        "metadata": {"attribute": "neighborhoods"}
    },
    {
        "id": "class_year",
        "text": """Attribute: Class Year Eligibility by Residence Hall
 
First-year students are housed in: Boland Hall, Brewster Hall, Brockway Hall, Day Hall, DellPlain Hall, Ernie Davis Hall, Haven Hall, Lawrinson Hall, Sadler Hall, Shaw Hall, Watson Hall.
Sophomore housing options include: Booth Hall, Haven Hall, DellPlain Hall, Oren Lyons Hall, Shaw Hall, Walnut Hall, Washington Arms, Orange Hall, 801 University Ave, 727 South Crouse Ave, South Campus apartments, Skyhalls.
Transfer students are typically housed in: Skyhall I, Skyhall II, Skyhall III, South Campus apartments.""",
        "metadata": {"attribute": "class_year"}
    },
    {
        "id": "security",
        "text": """Attribute: Security Features
 
All Syracuse University residence halls use an ID card swipe access system and are locked at all times. Only resident students and approved guests may enter. Each hall has residential community security officers stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms and remain locked. Every residence hall is equipped with fire suppression sprinkler systems and smoke detectors in each student room and throughout all common areas.""",
        "metadata": {"attribute": "security"}
    },
    {
        "id": "furnishings",
        "text": """Attribute: Furnishings by Room Type
 
Standard residence hall rooms (singles, doubles, suites): Bed (XL twin), desk, desk chair, dresser, and closet per student. Suites also include a couch in the common room.
801 University Ave and 727 South Crouse Ave apartments: Bed (full), desk, desk chair, closet, and dresser per bedroom. Common areas include a couch and coffee table. Each apartment has a full modern kitchen (microwave not included). Each bedroom in 801 University Ave has a full private bathroom.
South Campus apartments: Fully furnished with all utilities included. Full kitchens are provided but students must supply their own cooking utensils and microwave.""",
        "metadata": {"attribute": "furnishings"}
    },
    # TODO: Add more chunks as your data person compiles them:
    # - "walking_distances" (distances from each hall to key landmarks)
    # - "amenities" (laundry, fitness, study lounges per hall)
    # - "pricing" (room rates by hall and room type)
    # - "llc_info" (Living Learning Communities and which halls host them)
]
 
 
# ============================================================
# 2. BUILD THE CHROMADB
# ============================================================
# PersistentClient saves the database to disk so you only run this once.
# The Streamlit app will open this same folder to query it.
 
DB_PATH = "./chroma_db"
 
# Clear old DB if re-running
if os.path.exists(DB_PATH):
    import shutil
    shutil.rmtree(DB_PATH)
    print("Cleared old database.")
 
client = chromadb.PersistentClient(path=DB_PATH)
 
collection = client.get_or_create_collection(
    name="su_housing",
    # ChromaDB uses all-MiniLM-L6-v2 by default (384-dim embeddings)
    # This is fine for our use case — no need to change it
)
 
# ============================================================
# 3. ADD CHUNKS TO THE COLLECTION
# ============================================================
collection.add(
    ids=[chunk["id"] for chunk in housing_chunks],
    documents=[chunk["text"] for chunk in housing_chunks],
    metadatas=[chunk["metadata"] for chunk in housing_chunks],
)
 
print(f"Added {collection.count()} chunks to the collection.")
print("Database saved to:", DB_PATH)
 
# Quick test: try a query
results = collection.query(
    query_texts=["Which dorms have private bathrooms?"],
    n_results=3
)
print("\nTest query: 'Which dorms have private bathrooms?'")
print("Top results:")
for i, doc_id in enumerate(results["ids"][0]):
    print(f"  {i+1}. {doc_id}")