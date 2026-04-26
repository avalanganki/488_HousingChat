try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import chromadb
import os
import shutil

housing_chunks = [
    # ── Boland Hall ──
    {
        "id": "boland_hall",
        "text": (
            "Boland Hall\n"
            "Address: 401 Van Buren Street\n"
            "Location: North Campus\n"
            "Class Year Eligibility: First Year/Freshman\n"
            "Closest Dining Hall: Brockway Dining Hall (connected to building)\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: Boland Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Communal shared bathrooms (single-gender room with multiple stalls, sinks, and showers)\n"
            "Room Types Available: Singles, Split Doubles\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, laundry in basement, connected to Brockway Dining Hall.\n"
            "Living Learning Communities (LLCs): Creative Writing LLC, Design LLC, Music & Culture LLC\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "- Split Double: $5,760\n"
            "First Year Housing Process: The majority of the incoming class will be placed randomly into open double "
            "and split double rooms. Some first-year students will be placed into 4-person rooms. Housing is guaranteed "
            "for all first-year students."
        ),
        "metadata": {"hall": "Boland Hall", "location": "North Campus", "eligibility": "Freshman"}
    },

    # ── Booth Hall ──
    {
        "id": "booth_hall",
        "text": (
            "Booth Hall\n"
            "Address: 505 Comstock Avenue\n"
            "Location: North Campus\n"
            "Class Year Eligibility: Second Year/Sophomore\n"
            "Closest Dining Hall: Ernie Davis Dining Hall\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: Booth Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Communal shared bathrooms (single-gender room with multiple stalls, sinks, and showers)\n"
            "Room Types Available: Singles, Open Doubles, Split Doubles, Two-Person Suites, Four-Person Suites\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, communal kitchen on each floor, laundry in basement.\n"
            "Living Learning Communities (LLCs): None\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "- Open Double: $5,240\n"
            "- Split Double: $5,760\n"
            "- Suites (all other locations): $5,910"
        ),
        "metadata": {"hall": "Booth Hall", "location": "North Campus", "eligibility": "Sophomore"}
    },

    # ── Brewster Hall ──
    {
        "id": "brewster_hall",
        "text": (
            "Brewster Hall\n"
            "Address: 401 Van Buren Street\n"
            "Location: North Campus\n"
            "Class Year Eligibility: First Year/Freshman\n"
            "Closest Dining Hall: Brockway Dining Hall (connected to building)\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: Brewster Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Communal shared bathrooms (single-gender room with multiple stalls, sinks, and showers)\n"
            "Room Types Available: Singles, Split Doubles, Four-Person Suites\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, laundry in basement, connected to Brockway Dining Hall.\n"
            "Living Learning Communities (LLCs): None\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "- Split Double: $5,760\n"
            "- Suites (all other locations): $5,910\n"
            "First Year Housing Process: The majority of the incoming class will be placed randomly into open double "
            "and split double rooms. Some first-year students will be placed into 4-person rooms. Housing is guaranteed "
            "for all first-year students."
        ),
        "metadata": {"hall": "Brewster Hall", "location": "North Campus", "eligibility": "Freshman"}
    },

    # ── Brockway Hall ──
    {
        "id": "brockway_hall",
        "text": (
            "Brockway Hall\n"
            "Address: 401 Van Buren Street\n"
            "Location: North Campus\n"
            "Class Year Eligibility: First Year/Freshman\n"
            "Closest Dining Hall: Brockway Dining Hall (connected to building)\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: Brockway Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Communal shared bathrooms (single-gender room with multiple stalls, sinks, and showers)\n"
            "Room Types Available: Singles, Open Doubles\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, laundry in basement, air-conditioned building, "
            "computer cluster, connected to Brockway Dining Hall.\n"
            "Living Learning Communities (LLCs): None\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "- Open Double: $5,240\n"
            "First Year Housing Process: The majority of the incoming class will be placed randomly into open double "
            "and split double rooms. Some first-year students will be placed into 4-person rooms. Housing is guaranteed "
            "for all first-year students."
        ),
        "metadata": {"hall": "Brockway Hall", "location": "North Campus", "eligibility": "Freshman"}
    },

    # ── Day Hall ──
    {
        "id": "day_hall",
        "text": (
            "Day Hall\n"
            "Address: 1 Mount Olympus Drive\n"
            "Location: North Campus\n"
            "Class Year Eligibility: First Year/Freshman\n"
            "Closest Dining Hall: Graham Dining Hall (connected to building)\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: Day Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Pod-style shared bathrooms (individual lockable rooms with shower, toilet, sink)\n"
            "Room Types Available: Singles, Open Doubles, Split Doubles\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, laundry in basement, connected to Graham Dining Hall.\n"
            "Living Learning Communities (LLCs): Communication and Rhetorical Studies LLC, International Relations LLC, "
            "Multicultural LLC (MLLC), Sport Analytics LLC, Sport Management LLC\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "- Open Double: $5,240\n"
            "- Split Double: $5,760\n"
            "First Year Housing Process: The majority of the incoming class will be placed randomly into open double "
            "and split double rooms. Some first-year students will be placed into 4-person rooms. Housing is guaranteed "
            "for all first-year students."
        ),
        "metadata": {"hall": "Day Hall", "location": "North Campus", "eligibility": "Freshman"}
    },

    # ── DellPlain Hall ──
    {
        "id": "dellplain_hall",
        "text": (
            "DellPlain Hall\n"
            "Address: 601 Comstock Avenue\n"
            "Location: North Campus\n"
            "Class Year Eligibility: First Year/Freshman, Second Year/Sophomore\n"
            "Closest Dining Hall: Ernie Davis Dining Hall\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: DellPlain Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Pod-style shared bathrooms (individual lockable rooms with shower, toilet, sink)\n"
            "Room Types Available: Singles, Open Doubles, Split Doubles\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, laundry on first floor.\n"
            "Living Learning Communities (LLCs): Barbara Glazer Weinstein & Jerome S. Glazer Creativity, Innovation, "
            "and Entrepreneurship (CIE) LLC, LGBTQ LLC (open to freshmen and sophomores), Whitman Leadership LLC\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "- Open Double: $5,240\n"
            "- Split Double: $5,760\n"
            "First Year Housing Process: The majority of the incoming class will be placed randomly into open double "
            "and split double rooms. Some first-year students will be placed into 4-person rooms. Housing is guaranteed "
            "for all first-year students."
        ),
        "metadata": {"hall": "DellPlain Hall", "location": "North Campus", "eligibility": "Freshman, Sophomore"}
    },

    # ── Ernie Davis Hall ──
    {
        "id": "ernie_davis_hall",
        "text": (
            "Ernie Davis Hall\n"
            "Address: 619 Comstock Avenue\n"
            "Location: North Campus\n"
            "Class Year Eligibility: First Year/Freshman\n"
            "Closest Dining Hall: Ernie Davis Dining Hall (connected to building)\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: Ernie Davis Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Pod-style shared bathrooms (individual lockable rooms with shower, toilet, sink)\n"
            "Room Types Available: Singles, Split Doubles\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, laundry on each floor, in-building fitness center, "
            "connected to Ernie Davis Dining Hall.\n"
            "Living Learning Communities (LLCs): MORE in Architecture LLC (sophomore), MORE in Multicultural LLC "
            "(MORE MLLC) (sophomore)\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "- Split Double: $5,760\n"
            "First Year Housing Process: The majority of the incoming class will be placed randomly into open double "
            "and split double rooms. Some first-year students will be placed into 4-person rooms. Housing is guaranteed "
            "for all first-year students."
        ),
        "metadata": {"hall": "Ernie Davis Hall", "location": "North Campus", "eligibility": "Freshman"}
    },

    # ── Flint Hall ──
    {
        "id": "flint_hall",
        "text": (
            "Flint Hall\n"
            "Address: 2 Mount Olympus Drive\n"
            "Location: North Campus\n"
            "Class Year Eligibility: First Year/Freshman\n"
            "Closest Dining Hall: Graham Dining Hall\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: Flint Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Pod-style shared bathrooms (individual lockable rooms with shower, toilet, sink)\n"
            "Room Types Available: Singles, Open Doubles\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, team study rooms, laundry in basement.\n"
            "Living Learning Communities (LLCs): None\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "- Open Double: $5,240\n"
            "First Year Housing Process: The majority of the incoming class will be placed randomly into open double "
            "and split double rooms. Some first-year students will be placed into 4-person rooms. Housing is guaranteed "
            "for all first-year students."
        ),
        "metadata": {"hall": "Flint Hall", "location": "North Campus", "eligibility": "Freshman"}
    },

    # ── Haven Hall ──
    {
        "id": "haven_hall",
        "text": (
            "Haven Hall\n"
            "Address: 400 Comstock Avenue\n"
            "Location: North Campus\n"
            "Class Year Eligibility: First Year/Freshman, Second Year/Sophomore\n"
            "Closest Dining Hall: Ernie Davis Dining Hall\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: Haven Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Pod-style shared bathrooms (individual lockable rooms with shower, toilet, sink)\n"
            "Room Types Available: Singles, Open Doubles, Split Doubles, One-Person Suites, Two-Person Suites, "
            "Four-Person Suites\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, 24-hour quiet study room, laundry in basement.\n"
            "Living Learning Communities (LLCs): Esports LLC, Indigenous LLC (open to freshmen and sophomores), "
            "International LLC\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "- Open Double: $5,240\n"
            "- Split Double: $5,760\n"
            "- 1-person suite (Haven Hall): $7,320\n"
            "- 2-person suite (Haven Hall): $6,800\n"
            "- 2-person suite with bath (Haven Hall): $6,800\n"
            "- Four-Person Suite (all other locations rate): $5,910\n"
            "First Year Housing Process: The majority of the incoming class will be placed randomly into open double "
            "and split double rooms. Some first-year students will be placed into 4-person rooms. Housing is guaranteed "
            "for all first-year students."
        ),
        "metadata": {"hall": "Haven Hall", "location": "North Campus", "eligibility": "Freshman, Sophomore"}
    },

    # ── Lawrinson Hall ──
    {
        "id": "lawrinson_hall",
        "text": (
            "Lawrinson Hall\n"
            "Address: 303 Stadium Place\n"
            "Location: North Campus\n"
            "Class Year Eligibility: First Year/Freshman\n"
            "Closest Dining Hall: Sadler Dining Hall\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: Lawrinson Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Pod-style shared bathrooms (individual lockable rooms with shower, toilet, sink)\n"
            "Room Types Available: Singles, Split Doubles, Corner Doubles\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, laundry on each floor, music room, "
            "penthouse gathering space.\n"
            "Living Learning Communities (LLCs): Education HIVE LLC, Leadership LLC, Maxwell LLC, ROTC LLC\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "- Split Double: $5,760\n"
            "First Year Housing Process: The majority of the incoming class will be placed randomly into open double "
            "and split double rooms. Some first-year students will be placed into 4-person rooms. Housing is guaranteed "
            "for all first-year students."
        ),
        "metadata": {"hall": "Lawrinson Hall", "location": "North Campus", "eligibility": "Freshman"}
    },

    # ── Milton Hall ──
    {
        "id": "milton_hall",
        "text": (
            "Milton Hall\n"
            "Address: 727 South Crouse Avenue\n"
            "Location: North Campus\n"
            "Class Year Eligibility: Second Year/Sophomore\n"
            "Closest Dining Hall: Orange Dining Hall\n"
            "Meal Plan Requirement: Required minimum plan is the Value Dining Dollar Plan ($500). Optional upgrades: "
            "Deluxe Dining Dollar Plan ($1,250), Daily Dining Dollar Plan ($1,750), Block 85, Block 130, Orange Unlimited.\n"
            "Security: Milton Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Private, in-room bathrooms\n"
            "Room Types Available: Studio Apartments, Single-Bedroom Apartments, Two-Bedroom Apartments, "
            "Four-Bedroom Apartments\n"
            "Furnishings: Furnishings vary by apartment type but typically include a bed (full size, not twin XL), "
            "desk and desk chair, closet, and dresser per bedroom, as well as a couch and coffee table in the common "
            "living space. Each apartment includes a full, modern kitchen but does not include a microwave. "
            "Each bedroom has a full bathroom.\n"
            "Amenities: Team study rooms, entertainment area, in-building fitness center, laundry in basement.\n"
            "Living Learning Communities (LLCs): None\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Modern Studio (1 student): $8,560\n"
            "- Modern 1-bedroom (1 student): $8,880\n"
            "- Modern 2-bedroom (2 students): $8,360\n"
            "- Modern 4-bedroom (4 students): $8,200"
        ),
        "metadata": {"hall": "Milton Hall", "location": "North Campus", "eligibility": "Sophomore"}
    },

    # ── Orange Hall ──
    {
        "id": "orange_hall",
        "text": (
            "Orange Hall\n"
            "Address: 801 University Avenue\n"
            "Location: North Campus\n"
            "Class Year Eligibility: Second Year/Sophomore\n"
            "Closest Dining Hall: Orange Dining Hall (connected to building)\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: Orange Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Private, in-room bathrooms\n"
            "Room Types Available: Modern Open Doubles with Bathroom, Modern Open Triples with Bathroom\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, laundry on each floor, connected to Orange Dining Hall.\n"
            "Living Learning Communities (LLCs): None\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Modern Open Double with Bath: $7,520\n"
            "- Modern Open Triple with Bath: $7,320"
        ),
        "metadata": {"hall": "Orange Hall", "location": "North Campus", "eligibility": "Sophomore"}
    },

    # ── Oren Lyons Hall ──
    {
        "id": "oren_lyons_hall",
        "text": (
            "Oren Lyons Hall\n"
            "Address: 401 Euclid Avenue\n"
            "Location: North Campus\n"
            "Class Year Eligibility: Second Year/Sophomore\n"
            "Closest Dining Hall: Shaw Dining Hall\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: Oren Lyons Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Pod-style shared bathrooms (individual lockable rooms with shower, toilet, sink)\n"
            "Room Types Available: Singles, Open Doubles, Open Triples, Three-Person Suites\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, laundry in basement.\n"
            "Living Learning Communities (LLCs): None\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "- Open Double: $5,240\n"
            "- Open Triple: $4,380\n"
            "- Suites (all other locations): $5,910"
        ),
        "metadata": {"hall": "Oren Lyons Hall", "location": "North Campus", "eligibility": "Sophomore"}
    },

    # ── Sadler Hall ──
    {
        "id": "sadler_hall",
        "text": (
            "Sadler Hall\n"
            "Address: 1000 Irving Avenue\n"
            "Location: North Campus\n"
            "Class Year Eligibility: First Year/Freshman\n"
            "Closest Dining Hall: Sadler Dining Hall (connected to building)\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: Sadler Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Pod-style shared bathrooms (individual lockable rooms with shower, toilet, sink)\n"
            "Room Types Available: Singles, Open Doubles, Split Doubles\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, team study rooms, communal kitchenette on each floor, "
            "laundry in basement, connected to Sadler Dining Hall.\n"
            "Living Learning Communities (LLCs): Honors LLC\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "- Open Double: $5,240\n"
            "- Split Double: $5,760\n"
            "First Year Housing Process: The majority of the incoming class will be placed randomly into open double "
            "and split double rooms. Some first-year students will be placed into 4-person rooms. Housing is guaranteed "
            "for all first-year students."
        ),
        "metadata": {"hall": "Sadler Hall", "location": "North Campus", "eligibility": "Freshman"}
    },

    # ── Shaw Hall ──
    {
        "id": "shaw_hall",
        "text": (
            "Shaw Hall\n"
            "Address: 201 Euclid Avenue\n"
            "Location: North Campus\n"
            "Class Year Eligibility: First Year/Freshman, Second Year/Sophomore\n"
            "Closest Dining Hall: Shaw Dining Hall (connected to building)\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: Shaw Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Pod-style shared bathrooms (individual lockable rooms with shower, toilet, sink)\n"
            "Room Types Available: Singles, Open Doubles, Split Doubles\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, laundry in basement, connected to Shaw Dining Hall.\n"
            "Living Learning Communities (LLCs): Architecture LLC, Engineering and Computer Science LLC, "
            "Exercise Science LLC, Psychology in Action LLC, Science, Technology, and Math LLC\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "- Open Double: $5,240\n"
            "- Split Double: $5,760\n"
            "First Year Housing Process: The majority of the incoming class will be placed randomly into open double "
            "and split double rooms. Some first-year students will be placed into 4-person rooms. Housing is guaranteed "
            "for all first-year students."
        ),
        "metadata": {"hall": "Shaw Hall", "location": "North Campus", "eligibility": "Freshman, Sophomore"}
    },

    # ── Skyhall I ──
    {
        "id": "skyhall_1",
        "text": (
            "Skyhall I\n"
            "Address: 410-430 Lambreth Lane\n"
            "Location: South Campus\n"
            "Class Year Eligibility: Second Year/Sophomore, Transfer Students\n"
            "Closest Dining Hall: Goldstein Student Center (South Campus)\n"
            "Meal Plan Requirement: Required minimum plan is the Deluxe Dining Dollar Plan ($1,250). Optional upgrades: "
            "Daily Dining Dollar Plan ($1,750), Block 85, Block 130, Orange Unlimited.\n"
            "Security: Skyhall I uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Pod-style shared bathrooms (individual lockable rooms with shower, toilet, sink)\n"
            "Room Types Available: Singles\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Laundry in basement and on each floor.\n"
            "Living Learning Communities (LLCs): None\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "Transfer Student Housing: Incoming transfer students are typically placed within open-double rooms and "
            "two- and three-person apartments. Housing is not guaranteed for all transfer students. On-campus housing "
            "for transfer students is managed on a space-available basis until all allotted spaces have been filled.\n"
            "Getting to and from South Campus: Syracuse University shuttles run regularly throughout the day bringing "
            "students to and from South Campus and North Campus."
        ),
        "metadata": {"hall": "Skyhall I", "location": "South Campus", "eligibility": "Sophomore, Transfer"}
    },

    # ── Skyhall II ──
    {
        "id": "skyhall_2",
        "text": (
            "Skyhall II\n"
            "Address: 410-430 Lambreth Lane\n"
            "Location: South Campus\n"
            "Class Year Eligibility: Second Year/Sophomore, Transfer Students\n"
            "Closest Dining Hall: Goldstein Student Center (South Campus)\n"
            "Meal Plan Requirement: Required minimum plan is the Deluxe Dining Dollar Plan ($1,250). Optional upgrades: "
            "Daily Dining Dollar Plan ($1,750), Block 85, Block 130, Orange Unlimited.\n"
            "Security: Skyhall II uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Pod-style shared bathrooms (individual lockable rooms with shower, toilet, sink)\n"
            "Room Types Available: Singles\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Laundry in basement and on each floor.\n"
            "Living Learning Communities (LLCs): None\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "Transfer Student Housing: Incoming transfer students are typically placed within open-double rooms and "
            "two- and three-person apartments. Housing is not guaranteed for all transfer students. On-campus housing "
            "for transfer students is managed on a space-available basis until all allotted spaces have been filled.\n"
            "Getting to and from South Campus: Syracuse University shuttles run regularly throughout the day bringing "
            "students to and from South Campus and North Campus."
        ),
        "metadata": {"hall": "Skyhall II", "location": "South Campus", "eligibility": "Sophomore, Transfer"}
    },

    # ── Skyhall III ──
    {
        "id": "skyhall_3",
        "text": (
            "Skyhall III\n"
            "Address: 410-430 Lambreth Lane\n"
            "Location: South Campus\n"
            "Class Year Eligibility: Second Year/Sophomore, Transfer Students\n"
            "Closest Dining Hall: Goldstein Student Center (South Campus)\n"
            "Meal Plan Requirement: Required minimum plan is the Deluxe Dining Dollar Plan ($1,250). Optional upgrades: "
            "Daily Dining Dollar Plan ($1,750), Block 85, Block 130, Orange Unlimited.\n"
            "Security: Skyhall III uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Pod-style shared bathrooms (individual lockable rooms with shower, toilet, sink)\n"
            "Room Types Available: Singles\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Laundry in basement and on each floor.\n"
            "Living Learning Communities (LLCs): None\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "Transfer Student Housing: Incoming transfer students are typically placed within open-double rooms and "
            "two- and three-person apartments. Housing is not guaranteed for all transfer students. On-campus housing "
            "for transfer students is managed on a space-available basis until all allotted spaces have been filled.\n"
            "Getting to and from South Campus: Syracuse University shuttles run regularly throughout the day bringing "
            "students to and from South Campus and North Campus."
        ),
        "metadata": {"hall": "Skyhall III", "location": "South Campus", "eligibility": "Sophomore, Transfer"}
    },

    # ── South Campus Apartments ──
    {
        "id": "south_campus_apartments",
        "text": (
            "South Campus Apartments\n"
            "Location: South Campus\n"
            "Class Year Eligibility: Second Year/Sophomore, Third Year/Junior, Fourth Year/Senior, Transfer Students\n"
            "Closest Dining Hall: Goldstein Student Center (South Campus)\n"
            "Meal Plan Requirement: None required. Optional plans: Value Dining Dollar Plan ($500), Deluxe Dining Dollar "
            "Plan ($1,250), Daily Dining Dollar Plan ($1,750), Block 85, Block 130, Orange Unlimited.\n"
            "Security: South Campus Apartments use an ID card swipe access system and are locked at all times. "
            "Only resident students and approved guests may enter. Each building has residential community security "
            "officers stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible "
            "alarms and remain locked. Buildings are equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Private, in-room bathrooms (one bathroom per apartment)\n"
            "Room Types Available: One-Bedroom Apartments, Two-Bedroom Apartments, Three-Bedroom Apartments\n"
            "Apartment Streets and Apartment Types:\n"
            "- Chinook Drive: Two-Bedroom apartments, Three-Bedroom apartments\n"
            "- Farm Acre Road: Two-Bedroom apartments, Three-Bedroom apartments\n"
            "- Lambreth Lane: Two-Bedroom apartments, Three-Bedroom apartments\n"
            "- Slocum Heights: One-Bedroom apartments\n"
            "- Small Road: Two-Bedroom apartments, Three-Bedroom apartments\n"
            "- Winding Ridge Road: Two-Bedroom apartments\n"
            "Furnishings: Each apartment is fully furnished. Beds are full XL size (not twin XL). Each apartment "
            "includes a full kitchen, one bathroom, and private bedrooms. Utilities are included.\n"
            "Amenities: Utilities included, fully furnished, full kitchen, one bathroom, private bedrooms, "
            "on-site parking available.\n"
            "Living Learning Communities (LLCs): None\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- 1-bedroom (1 student): $7,210\n"
            "- 2-bedroom (2 students): $6,690\n"
            "- 3-bedroom (3 students): $6,220\n"
            "Transfer Student Housing: Incoming transfer students are typically placed within open-double rooms and "
            "two- and three-person apartments. Housing is not guaranteed for all transfer students. On-campus housing "
            "for transfer students is managed on a space-available basis until all allotted spaces have been filled.\n"
            "Getting to and from South Campus: Syracuse University shuttles run regularly throughout the day bringing "
            "students to and from South Campus and North Campus."
        ),
        "metadata": {"hall": "South Campus Apartments", "location": "South Campus", "eligibility": "Sophomore, Junior, Senior, Transfer"}
    },

    # ── Walnut Hall ──
    {
        "id": "walnut_hall",
        "text": (
            "Walnut Hall\n"
            "Address: 400 Comstock Avenue\n"
            "Location: North Campus\n"
            "Class Year Eligibility: Second Year/Sophomore\n"
            "Closest Dining Hall: Ernie Davis Dining Hall\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: Walnut Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Pod-style shared bathrooms (individual lockable rooms with shower, toilet, sink)\n"
            "Room Types Available: Singles, Open Doubles\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, laundry in basement.\n"
            "Living Learning Communities (LLCs): None\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Regular Single: $6,170\n"
            "- Open Double: $5,240"
        ),
        "metadata": {"hall": "Walnut Hall", "location": "North Campus", "eligibility": "Sophomore"}
    },

    # ── Washington Arms ──
    {
        "id": "washington_arms",
        "text": (
            "Washington Arms\n"
            "Address: 621 Walnut Avenue\n"
            "Location: North Campus\n"
            "Class Year Eligibility: Second Year/Sophomore\n"
            "Closest Dining Hall: Ernie Davis Dining Hall\n"
            "Meal Plan Requirement: Orange Unlimited (required for all North Campus first and second year residents)\n"
            "Security: Washington Arms uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Private, in-room bathrooms\n"
            "Room Types Available: Open Doubles with Bathroom, Two-Person Suites with Bathroom, "
            "Three-Person Suites with Bathroom\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, communal kitchen on each floor, laundry in basement.\n"
            "Living Learning Communities (LLCs): None\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- Open Double with Bath: $5,760\n"
            "- 2-person suite with bath (Washington Arms): $6,800\n"
            "- 3-person suite with bath (Washington Arms): $6,170"
        ),
        "metadata": {"hall": "Washington Arms", "location": "North Campus", "eligibility": "Sophomore"}
    },

    # ── Watson Hall ──
    {
        "id": "watson_hall",
        "text": (
            "Watson Hall\n"
            "Address: 405 University Place\n"
            "Location: North Campus\n"
            "Class Year Eligibility: Not specified (check with Housing Office)\n"
            "Closest Dining Hall: Ernie Davis Dining Hall\n"
            "Meal Plan Requirement: Orange Unlimited (required for North Campus residents)\n"
            "Security: Watson Hall uses an ID card swipe access system and is locked at all times. "
            "Only resident students and approved guests may enter. Residential community security officers are "
            "stationed at the main entrance 24 hours a day, seven days a week. Secondary exits have audible alarms "
            "and remain locked. The building is equipped with fire suppression sprinkler systems and smoke detectors "
            "in each student room and throughout all common areas.\n"
            "Bathroom Type: Pod-style shared bathrooms (individual lockable rooms with shower, toilet, sink)\n"
            "Room Types Available: Two-Person Suites, Three-Person Suites, Four-Person Suites, Six-Person Suites\n"
            "Furnishings: Each student room is furnished with a twin XL bed, desk, desk chair, dresser(s), "
            "and closet/wardrobe for each student.\n"
            "Amenities: Communal study/social lounge on each floor, communal kitchenette on 2nd and 4th floors, "
            "laundry in basement.\n"
            "Living Learning Communities (LLCs): MORE in Multicultural LLC (MORE MLLC) (sophomore)\n"
            "Pricing (2025-2026, per student, per semester):\n"
            "- 2-person suite with bath (Watson Hall): $6,800\n"
            "- Suites (all other locations): $5,910"
        ),
        "metadata": {"hall": "Watson Hall", "location": "North Campus", "eligibility": "Not specified"}
    },

    # ── General Policies: Housing Application & Roommate Selection ──
    {
        "id": "general_housing_process",
        "text": (
            "General Housing Policies and Processes\n\n"
            "Applying for Housing (Returning Students):\n"
            "Room Selection is a lottery process where eligible returning students select their housing assignment "
            "for the next academic year through the Housing Portal (via MySlice). Room selection is separated into rounds. "
            "Once students select a room, they are done and do not move on to later rounds.\n\n"
            "Selecting Roommate(s):\n"
            "The Roommate Matching process will become available once you complete the application. You will be able "
            "to search for compatible roommates or locate specific students you already know to form roommate groups. "
            "Roommate Matching will remain open throughout Room Selection to allow students to make changes to their "
            "roommate groups as needed. Rooms must be filled to capacity during selection."
        ),
        "metadata": {"hall": "General", "location": "N/A", "eligibility": "All"}
    },

    # ── General Policies: Meal Plans ──
    {
        "id": "meal_plan_details",
        "text": (
            "Meal Plan Details\n\n"
            "Orange Unlimited Plan: Provides unlimited access to North Campus dining centers and 10 guest meals per "
            "semester for friends and family. Pop-ups, study breaks, and theme dinners are also included. Includes "
            "$330 of Meal Plan Dining Dollars.\n\n"
            "Block 130 Plan: Provides 130 meals per semester in North Campus dining centers. Divided evenly, this "
            "equates to 9 meals per week. Includes $200 of Meal Plan Dining Dollars.\n\n"
            "Block 85 Plan: Provides 85 meals per semester in North Campus dining centers. Divided evenly, this "
            "equates to 6 meals per week. Includes $200 of Meal Plan Dining Dollars.\n\n"
            "Daily Dining Dollars Plan: Provides a Dining Dollars account of $1,750.\n\n"
            "Deluxe Dining Dollars Plan: Provides a Dining Dollars account of $1,250.\n\n"
            "Value Dining Dollars Plan: Provides a Dining Dollars account of $500.\n\n"
            "Meal Plan Eligibility and Requirements Summary:\n"
            "- First and Second Year Residence Hall Students (North Campus): Must have Orange Unlimited.\n"
            "- Third and Fourth Year Residence Hall Students (North Campus): Required minimum is Block 85. "
            "May upgrade to Block 130 or Orange Unlimited.\n"
            "- Skyhall Residents: Required minimum is Deluxe Dining Dollar Plan. May upgrade to Daily Dining Dollar Plan, "
            "Block 85, Block 130, or Orange Unlimited.\n"
            "- Milton Hall Residents: Required minimum is Value Dining Dollar Plan. May upgrade to Deluxe Dining Dollar Plan, "
            "Daily Dining Dollar Plan, Block 85, Block 130, or Orange Unlimited.\n"
            "- South Campus Apartment Residents: No meal plan required. All plans available as optional.\n"
            "- Off-Campus Students: No meal plan required. All plans available as optional."
        ),
        "metadata": {"hall": "General", "location": "N/A", "eligibility": "All"}
    },

    # ── General Policies: Dining Hall Locations ──
    {
        "id": "dining_hall_locations",
        "text": (
            "Dining Hall Locations\n\n"
            "- Ernie Davis Dining Hall: North Campus (near Booth, DellPlain, Ernie Davis, Haven, Watson, Walnut, Washington Arms)\n"
            "- Sadler Dining Hall: North Campus (near Sadler, Lawrinson)\n"
            "- Graham Dining Hall: North Campus (near Day, Flint)\n"
            "- Brockway Dining Hall: North Campus (near Boland, Brockway, Brewster)\n"
            "- Shaw Dining Hall: North Campus (near Shaw, Oren Lyons)\n"
            "- Orange Dining Hall: North Campus (near Orange, Milton)\n"
            "- Goldstein Student Center: South Campus (near Skyhall I, Skyhall II, Skyhall III, South Campus Apartments)\n\n"
            "An unlimited food plan is required for all students living in North Campus Residence Halls. "
            "South Campus Residents may choose a meal plan but are not required to have one."
        ),
        "metadata": {"hall": "General", "location": "N/A", "eligibility": "All"}
    },

    # ── Off-Campus Housing ──
    {
        "id": "off_campus_housing",
        "text": (
            "Off-Campus Housing\n"
            "Class Year Eligibility: Third Year/Junior, Fourth Year/Senior\n"
            "Location: Off-campus houses or apartments unaffiliated with the university.\n"
            "Meal Plan Requirement: None required. Optional plans: Value Dining Dollar Plan ($500), "
            "Deluxe Dining Dollar Plan ($1,250), Daily Dining Dollar Plan ($1,750), Block 85, Block 130, Orange Unlimited."
        ),
        "metadata": {"hall": "Off-Campus", "location": "Off-Campus", "eligibility": "Junior, Senior"}
    },
]

if __name__ == "__main__":
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")

    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="su_housing")

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