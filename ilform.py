from pandas import options
import streamlit as st
from datetime import date, timedelta
from database import InstructionSession, InstructionSessionSLO, Session  # your DB connection and table
from campuses import campus_list  # real campus list
from librarians import librarian_list  # real librarian list


min_date = date.today() + timedelta(days=14)

st.title("Add New Library Instruction Session")

# Extract names for dropdowns
campus_names = [campus['name'] for campus in campus_list]
librarian_names = [lib['name'] for lib in librarian_list]

with st.form("session_form"):
    first = st.text_input("First name:")
    last = st.text_input("Last name:")
    email=st.text_input("Email")
    date_1 = st.date_input("Session Request Date 1", min_value=min_date)
    date_2 = st.date_input("Session Request Date 2", min_value=min_date)
    
    type = st.selectbox(
        "Type",
        ("In-Person", "Asynchronous", "Synchronous")
    )
    
    campus = None
    if type == "In-Person":
        campus = st.selectbox(
            "Campus",
            sorted(campus_names)
        )
    
    librarian_presenter = st.selectbox(
        "Librarian",
        sorted(librarian_names)
    )
    
    course_code = st.text_input("Course Code (4 characters)")
    course_number = st.text_input("Course Number (4 characters)")
    
    slos = st.multiselect(
        "What would you like your students to learn during the session? (Choose up to three options)",
        (
            "Develop a research process",
            "Demonstrate effective search strategies",
            "Evaluate Information",
            "Develop an argument supported by evidence",
            "Use information ethically and legally"
        ),
        max_selections=3
    )
    
    submit = st.form_submit_button("Add Session")

if submit:
    # --- Validation for course code & number ---
    if len(course_code) != 4:
        st.error("Course Code must be exactly 4 characters.")
    elif len(course_number) != 4:
        st.error("Course Number must be exactly 4 characters.")
    else:
        session = Session()  # create DB session

        # Convert slos list to a comma-separated string for storage
    new_session = InstructionSession(
        date_1=date_1,
        date_2=date_2,
        first=first,
        last=last,
        email=email,
        campus=campus,
        librarian_presenter=librarian_presenter,
        course_code=course_code,
        course_number=course_number,
        type=type
    )

    session.add(new_session)
    session.flush()  # Gets new_session.id

# Add SLOs as separate rows in InstructionSessionSLO
    for slo in slos:
        slo_entry = InstructionSessionSLO(session_id=new_session.id, slo=slo)
        session.add(slo_entry)

    session.commit()
    session.close()
    st.success("New session added successfully!")