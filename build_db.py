# build_db.py
# Run ONCE to create the ChromaDB from housing data chunks.
# Usage: python build_db.py

try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import chromadb
import os
import shutil

# ============================================================
# 1. DEFINE ATTRIBUTE-BASED CHUNKS
# ============================================================

housing_chunks = [
    {
        "id": "security",
        "text": """Attribute: Security Features

All Syracuse University residence halls use an ID card swipe access system and are locked at all times. Only resident students and approved guests may enter. Each hall has residential community security officers stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms and remain locked. Every residence hall is equipped with fire suppression sprinkler systems and smoke detectors in each student room and throughout all common areas.""",
        "metadata": {"attribute": "security"}
    },
    {
        "id": "class_year",
        "text": """Attribute: Class Year Eligibility by Residence Hall

First Year/Freshman students are housed in: Boland Hall, Brockway Hall, Brewster Hall, Day Hall, Flint Hall, Sadler Hall, Haven Hall, DellPlain Hall, Ernie Davis Hall, Lawrinson Hall, Shaw Hall.
Second Year/Sophomore students are housed in: Booth Hall, Haven Hall, DellPlain Hall, Oren Lyons Hall, Shaw Hall, Walnut Hall, Washington Arms, Orange Hall, Milton Hall, South Campus Apartments, Skyhall I, Skyhall II, Skyhall III.
Third Year/Junior and Fourth Year/Senior students can live in: South Campus Apartments, Off-campus (unaffiliated with the university) houses or apartments.
Transfer Students are typically housed in: Skyhall I, Skyhall II, Skyhall III, South Campus Apartments.""",
        "metadata": {"attribute": "class_year"}
    },
    {
        "id": "neighborhoods",
        "text": """Attribute: Neighborhood and Location by Residence Hall

North Campus — North Neighborhood: Booth Hall, Haven Hall, Milton Hall, Orange Hall, Walnut Hall, Washington Arms.
North Campus — East Neighborhood: DellPlain Hall, Ernie Davis Hall, Oren Lyons Hall, Shaw Hall, Watson Hall.
North Campus — West Neighborhood: Boland Hall, Brewster Hall, Brockway Hall, Lawrinson Hall, Sadler Hall.
North Campus — Mount Olympus Neighborhood: Day Hall, Flint Hall.
South Campus: Skyhall I, Skyhall II, Skyhall III, South Campus Apartments.""",
        "metadata": {"attribute": "neighborhoods"}
    },
    {
        "id": "dining_access",
        "text": """Attribute: Closest Dining Hall Access by Residence Hall

Ernie Davis Dining Hall is closest to: Booth Hall, DellPlain Hall, Ernie Davis Hall, Haven Hall, Watson Hall, Walnut Hall, Washington Arms.
Sadler Dining Hall is closest to: Sadler Hall, Lawrinson Hall.
Graham Dining Hall is closest to: Day Hall, Flint Hall.
Brockway Dining Hall is closest to: Boland Hall, Brockway Hall, Brewster Hall.
Shaw Dining Hall is closest to: Shaw Hall, Oren Lyons Hall.
Orange Dining Hall is closest to: Orange Hall, Milton Hall.
Goldstein Student Center (South Campus) is closest to: Skyhall I, Skyhall II, Skyhall III, South Campus Apartments.
An unlimited food plan is required for all students living in North Campus Residence Halls. South Campus Residents may choose a meal plan but are not required to have one.""",
        "metadata": {"attribute": "dining_access"}
    },
    {
        "id": "bathroom_types",
        "text": """Attribute: Bathroom Types by Residence Hall

Pod-style shared bathrooms (individual lockable rooms with shower, toilet, sink): Day Hall, DellPlain Hall, Ernie Davis Hall, Flint Hall, Haven Hall, Lawrinson Hall, Oren Lyons Hall, Sadler Hall, Shaw Hall, Skyhall I, Skyhall II, Skyhall III, Walnut Hall, Watson Hall.
Communal shared bathrooms (single-gender room with multiple stalls, sinks, and showers): Boland Hall, Booth Hall, Brewster Hall, Brockway Hall.
Private, in-room bathrooms: Milton Hall, Orange Hall, Washington Arms, South Campus Apartments.""",
        "metadata": {"attribute": "bathroom_types"}
    },
    {
        "id": "room_types",
        "text": """Attribute: Room Types by Residence Hall

Singles: Boland Hall, Booth Hall, Brewster Hall, Brockway Hall, Day Hall, DellPlain Hall, Ernie Davis Hall, Flint Hall, Haven Hall, Lawrinson Hall, Oren Lyons Hall, Sadler Hall, Shaw Hall, Skyhall I, Skyhall II, Skyhall III, Walnut Hall, Watson Hall.
Open Doubles: Booth Hall, Brockway Hall, Day Hall, DellPlain Hall, Flint Hall, Haven Hall, Oren Lyons Hall, Sadler Hall, Shaw Hall, Walnut Hall, Watson Hall.
Open Doubles with Bathroom: Washington Arms.
Split Doubles: Boland Hall, Booth Hall, Brewster Hall, Day Hall, DellPlain Hall, Ernie Davis Hall, Haven Hall, Lawrinson Hall, Sadler Hall, Shaw Hall.
Corner Doubles: Lawrinson Hall.
Modern Open Doubles with Bathroom: Orange Hall.
Open Triples: Oren Lyons Hall.
Modern Open Triples with Bathroom: Orange Hall.
One-Person Suites: Haven Hall.
Two-Person Suites: Booth Hall, Haven Hall, Watson Hall.
Two-Person Suites with Bathroom: Washington Arms.
Three-Person Suites: Oren Lyons Hall, Watson Hall.
Three-Person Suites with Bathroom: Washington Arms.
Four-Person Suites: Booth Hall, Brewster Hall, Haven Hall, Watson Hall.
Six-Person Suites: Watson Hall.
Studio Apartments: Milton Hall.
Single-Bedroom Apartments: Milton Hall.
Two-Bedroom Apartments: Milton Hall.
Four-Bedroom Apartments: Milton Hall.""",
        "metadata": {"attribute": "room_types"}
    },
    {
        "id": "amenities",
        "text": """Attribute: Amenities by Residence Hall

Communal Study/Social Lounge on Each Floor: Boland Hall, Booth Hall, Brewster Hall, Brockway Hall, Day Hall, DellPlain Hall, Ernie Davis Hall, Flint Hall, Haven Hall, Lawrinson Hall, Orange Hall, Oren Lyons Hall, Sadler Hall, Shaw Hall, Walnut Hall, Washington Arms, Watson Hall.
Team Study Rooms: Flint Hall, Milton Hall, Sadler Hall.
24-hour Quiet Study Room: Haven Hall.
Communal Kitchen on Each Floor: Booth Hall, Washington Arms.
Communal Kitchenette on Each Floor: Sadler Hall.
Communal Kitchenette on 2nd and 4th Floors: Watson Hall.
Air-Conditioned Building: Brockway Hall.
Computer Cluster: Brockway Hall.
Music Room: Lawrinson Hall.
Entertainment Area: Milton Hall.
Penthouse Gathering Space: Lawrinson Hall.
In-Building Fitness Center: Ernie Davis Hall, Milton Hall.""",
        "metadata": {"attribute": "amenities"}
    },
    {
        "id": "laundry",
        "text": """Attribute: Laundry Facilities by Residence Hall

Laundry in Basement: Boland Hall, Booth Hall, Brewster Hall, Brockway Hall, Day Hall, Flint Hall, Haven Hall, Milton Hall, Oren Lyons Hall, Sadler Hall, Shaw Hall, Skyhall I, Skyhall II, Skyhall III, Walnut Hall, Washington Arms, Watson Hall.
Laundry on First Floor: DellPlain Hall.
Laundry on Each Floor: Ernie Davis Hall, Lawrinson Hall, Orange Hall, Skyhall I, Skyhall II, Skyhall III.""",
        "metadata": {"attribute": "laundry"}
    },
    {
        "id": "dining_connections",
        "text": """Attribute: Direct Dining Hall Connections by Residence Hall

Connected to Brockway Dining Hall: Boland Hall, Brewster Hall, Brockway Hall.
Connected to Graham Dining Hall: Day Hall.
Connected to Ernie Davis Dining Hall: Ernie Davis Hall.
Connected to Orange Dining Hall: Orange Hall.
Connected to Sadler Dining Hall: Sadler Hall.
Connected to Shaw Dining Hall: Shaw Hall.""",
        "metadata": {"attribute": "dining_connections"}
    },
    {
        "id": "furnishings",
        "text": """Attribute: Furnishings by Room Type

Each student room is furnished with a bed, desk, desk chair, dresser(s), and closet/wardrobe for each student.
All residence hall rooms contain twin XL beds unless otherwise stated.
Milton Hall apartments contain regular full beds.
South Campus apartments contain full XL beds.
Milton Hall Apartments: Furnishings vary by apartment type but typically include a bed (full), desk and desk chair, closet, and dresser per bedroom as well as a couch and coffee table in the common living space. Each apartment includes a full, modern kitchen but does not include a microwave. Each bedroom has a full bathroom.""",
        "metadata": {"attribute": "furnishings"}
    },
    {
        "id": "addresses",
        "text": """Attribute: Addresses by Residence Hall

Boland Hall — 401 Van Buren Street
Booth Hall — 505 Comstock Avenue
Brewster Hall — 401 Van Buren Street
Brockway Hall — 401 Van Buren Street
Day Hall — 1 Mount Olympus Drive
DellPlain Hall — 601 Comstock Avenue
Ernie Davis Hall — 619 Comstock Avenue
Flint Hall — 2 Mount Olympus Drive
Haven Hall — 400 Comstock Avenue
Lawrinson Hall — 303 Stadium Place
Milton Hall — 727 South Crouse Avenue
Orange Hall — 801 University Avenue
Oren Lyons Hall — 401 Euclid Avenue
Sadler Hall — 1000 Irving Avenue
Shaw Hall — 201 Euclid Avenue
Skyhall I — 410-430 Lambreth Lane
Skyhall II — 410-430 Lambreth Lane
Skyhall III — 410-430 Lambreth Lane
Walnut Hall — 400 Comstock Avenue
Washington Arms — 621 Walnut Avenue
Watson Hall — 405 University Place""",
        "metadata": {"attribute": "addresses"}
    },
    {
        "id": "llcs_freshman",
        "text": """Attribute: Living Learning Communities (LLCs) — Incoming Students

Architecture LLC — Shaw Hall
Barbara Glazer Weinstein & Jerome S. Glazer Creativity, Innovation, and Entrepreneurship (CIE) LLC — DellPlain Hall
Communication and Rhetorical Studies LLC — Day Hall
Creative Writing LLC — Boland Hall
Design LLC — Boland Hall
Education HIVE LLC — Lawrinson Hall
Engineering and Computer Science LLC — Shaw Hall
Esports LLC — Haven Hall
Exercise Science LLC — Shaw Hall
Honors LLC — Sadler Hall
Indigenous LLC — Haven Hall
International LLC — Haven Hall
International Relations LLC — Day Hall
Leadership LLC — Lawrinson Hall
LGBTQ LLC — DellPlain Hall
Maxwell LLC — Lawrinson Hall
Multicultural LLC (MLLC) — Day Hall
Music & Culture LLC — Boland Hall
Psychology in Action LLC — Shaw Hall
ROTC LLC — Lawrinson Hall
Science, Technology, and Math LLC — Shaw Hall
Sport Analytics LLC — Day Hall
Sport Management LLC — Day Hall
Whitman Leadership LLC — DellPlain Hall""",
        "metadata": {"attribute": "llcs_freshman"}
    },
    {
        "id": "llcs_sophomore",
        "text": """Attribute: Living Learning Communities (LLCs) — SophoMORE LLCs

Indigenous LLC (also open to sophomores) — Haven Hall
LGBTQ LLC (also open to sophomores) — DellPlain Hall
MORE in Architecture LLC — Ernie Davis Hall
MORE in Multicultural LLC (MORE MLLC) — Ernie Davis Hall / Watson Hall""",
        "metadata": {"attribute": "llcs_sophomore"}
    },
    {
        "id": "pricing",
        "text": """Attribute: Housing Pricing (2025-2026 Rates — Per Student, Per Semester)

Singles: Regular Single — $6,170. Large Single / Single with Bath — $6,800.
Doubles: Split Double / Large Open Double — $5,760. Open Double — $5,240. Open Double with Bath — $5,760. Large Open Double with Bath — $5,960. Modern Open Double with Bath — $7,520.
Triples: Open Triple — $4,380. Modern Open Triple with Bath — $7,320.
Suites: 1-person suite (Haven Hall) — $7,320. 2-person suite (Haven Hall) — $6,800. 2-person suite with bath (Haven, Washington Arms & Watson Halls) — $6,800. 3-person suite with bath (Washington Arms) — $6,170. Suites (all other locations) — $5,910.
Apartments: 1-bedroom (1 student) — $7,210. 2-bedroom (2 students) — $6,690. 3-bedroom (3 students) — $6,220. Modern Studio (1 student) — $8,560. Modern 1-bedroom (1 student) — $8,880. Modern 2-bedroom (2 students) — $8,360. Modern 4-bedroom (4 students) — $8,200.""",
        "metadata": {"attribute": "pricing"}
    },
    {
        "id": "freshman_housing_process",
        "text": """Attribute: First Year/Freshman Housing Process

The majority of the incoming class will be placed randomly into open double and split double rooms. Some first-year students will be placed into 4-person rooms. Incoming transfer students are typically placed within open-double rooms and two- and three-person apartments. Housing is guaranteed for all first-year students but is not guaranteed for all transfer students. On-campus housing for transfer students is managed on a space-available basis until all allotted spaces have been filled.""",
        "metadata": {"attribute": "freshman_housing_process"}
    },
    {
        "id": "returning_student_housing",
        "text": """Attribute: Applying for Housing (Returning Students)

Room Selection is a lottery process where eligible returning students select their housing assignment for the next academic year through the Housing Portal (via MySlice). Room selection is separated into rounds. Once students select a room, they are done and do not move on to later rounds. The Roommate Matching process will become available once you complete the application. You will be able to search for compatible roommates or locate specific students you already know to form roommate groups. Roommate Matching will remain open throughout Room Selection to allow students to make changes to their roommate groups as needed. Rooms must be filled to capacity during selection.""",
        "metadata": {"attribute": "returning_student_housing"}
    },
    {
        "id": "meal_plans",
        "text": """Attribute: Meal Plans

Unlimited Plan — Orange Unlimited: Provides unlimited access to the North Campus dining centers and 10 guest meals per semester for friends and family. Pop-ups, study breaks, and theme dinners are also included. Includes $330 of Meal Plan Dining Dollars.
Block Plans — Block 130: Provides 130 meals per semester in North Campus dining centers. Divided evenly, this equates to 9 meals per week. Includes $200 of Meal Plan Dining Dollars.
Block Plans — Block 85: Provides 85 meals per semester in North Campus dining centers. Divided evenly, this equates to 6 meals per week. Includes $200 of Meal Plan Dining Dollars.
Dining Dollar Plans — Daily Dining Dollars: Provides a Dining Dollars account of $1750.
Dining Dollar Plans — Deluxe Dining Dollars: Provides a Dining Dollars account of $1250.
Dining Dollar Plans — Value Dining Dollars: Provides a Dining Dollars account of $500.""",
        "metadata": {"attribute": "meal_plans"}
    },
    {
        "id": "meal_plan_requirements",
        "text": """Attribute: Meal Plan Eligibility and Requirements

Students residing in residence halls are required to have a University meal plan. Those students residing in South Campus apartments are not required to choose a meal plan.
First and Second Year Residence Hall Students: Must have Orange Unlimited.
Third and Fourth Year Residence Hall Students: Required minimum plan is Block 85. Optional upgrades: Block 130, Orange Unlimited.
Skyhall Residents: Required minimum plan is Deluxe Dining Dollar Plan. Optional upgrades: Daily Dining Dollar Plan, Block 85, Block 130, Orange Unlimited.
Milton Hall Residents: Required minimum plan is Value Dining Dollar Plan. Optional upgrades: Deluxe Dining Dollar Plan, Daily Dining Dollar Plan, Block 85, Block 130, Orange Unlimited.
South Campus Apartment Residents: No required minimum plan. Optional: Value Dining Dollar Plan, Deluxe Dining Dollar Plan, Daily Dining Dollar Plan, Block 85, Block 130, Orange Unlimited.
Off-Campus Students: No required minimum plan. Optional: Value Dining Dollar Plan, Deluxe Dining Dollar Plan, Daily Dining Dollar Plan, Block 85, Block 130, Orange Unlimited.""",
        "metadata": {"attribute": "meal_plan_requirements"}
    },
    {
        "id": "south_campus_apartments",
        "text": """Attribute: South Campus Apartment Details

South Campus Apartment Streets: Chinook Drive, Farm Acre Road, Lambreth Lane, Slocum Heights, Small Road, Winding Ridge Road.
Chinook Drive: Two Bedroom apartments, Three Bedroom apartments.
Farm Acre Road: Two Bedroom apartments, Three Bedroom apartments.
Lambreth Lane: Two Bedroom apartments, Three Bedroom apartments.
Slocum Heights: One Bedroom apartments.
Small Road: Two Bedroom apartments, Three Bedroom apartments.
Winding Ridge Road: Two Bedroom apartments.
South Campus Apartment Amenities: Utilities included, fully furnished, full kitchen, one bathroom, private bedrooms, on-site parking available.
South Campus apartments contain full XL beds.
Getting to and from South Campus: Syracuse University shuttles run regularly throughout the day bringing students to and from South Campus and North Campus.""",
        "metadata": {"attribute": "south_campus_apartments"}
    },
]

# ============================================================
# 2. SET UP CHROMADB WITH PERSISTENCE
# ============================================================

# Clear old database if it exists
if os.path.exists("./chroma_db"):
    shutil.rmtree("./chroma_db")

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="su_housing")

# ============================================================
# 3. ADD CHUNKS TO CHROMADB
# ============================================================

ids = [chunk["id"] for chunk in housing_chunks]
documents = [chunk["text"] for chunk in housing_chunks]
metadatas = [chunk["metadata"] for chunk in housing_chunks]

collection.add(
    ids=ids,
    documents=documents,
    metadatas=metadatas
)

print(f"Added {len(ids)} chunks to the collection.")
print(f"Database saved to: ./chroma_db")