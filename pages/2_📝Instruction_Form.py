from datetime import date
import streamlit as st
from database import InstructionSession, InstructionSessionSLO, Session
from campuses import campus_list
from librarians import librarian_list
import sendgrid
from sendgrid.helpers.mail import Mail

# --- CONFIG ---

min_date = date.today()  # Minimum date is today

# Map campuses to email addresses
campus_email_map = {
    "Highland": "cassidy.reid@austincc.edu",
    "Hays": "cassidy.reid@austincc.edu",
    "Elgin": "cassidy.reid@austincc.edu",
    "Cypress Creek": "cassidy.reid@austincc.edu",
    "Eastview": "cassidy.reid@austincc.edu",
    "Round Rock": "cassidy.reid@austincc.edu",
    # Add all needed campuses here
}

SENDGRID_API_KEY = "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"
FROM_EMAIL = "cassidy.reid@austincc.edu"  # or your verified SendGrid sender


# --- STREAMLIT FORM ---

st.title("Add New Library Instruction Session")

campus_names = [campus['name'] for campus in campus_list]
librarian_names = [lib['name'] for lib in librarian_list]

with st.form("session_form"):
    first = st.text_input("First name:")
    last = st.text_input("Last name:")
    email = st.text_input("Email")
    date_1 = st.date_input("Session Request Date 1", min_value=min_date)  # Min today
    date_2 = st.date_input("Session Request Date 2", min_value=min_date)  # Min today

    type = st.selectbox(
        "Type",
        ("In-Person", "Asynchronous", "Synchronous")
    )

    campus = None
    if type == "In-Person":
        campus = st.selectbox("Campus", sorted(campus_names))

    librarian_presenter = st.selectbox("Librarian", sorted(librarian_names))

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
    # --- VALIDATION ---
    if not first or not last or not email:
        st.error("Please fill out all required fields (First, Last, Email).")
    elif type == "In-Person" and not campus:
        st.error("Please select a campus for In-Person sessions.")
    elif len(course_code) != 4:
        st.error("Course Code must be exactly 4 characters.")
    elif len(course_number) != 4:
        st.error("Course Number must be exactly 4 characters.")
    else:
        session = Session()

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
        session.flush()  # Get ID for SLO linking

        for slo in slos:
            slo_entry = InstructionSessionSLO(session_id=new_session.id, slo=slo)
            session.add(slo_entry)

        session.commit()
        session.close()

# --- EMAIL LOGIC USING SENDGRID WEB API ---
recipient_email = campus_email_map.get(campus, "cassidy.reid@austincc.edu")
subject = f"New Library Instruction Request - {campus}"
body = f"""New Instruction Session Requested:

Name: {first} {last}
Email: {email}
Campus: {campus}
Type: {type}
Requested Dates: {date_1} or {date_2}
Course: {course_code}-{course_number}
Requested SLOs: {', '.join(slos)}
Requested Librarian: {librarian_presenter}

Please review this request in the system."""

message = Mail(
    from_email=FROM_EMAIL,
    to_emails=recipient_email,
    subject=subject,
    plain_text_content=body
)

try:
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    response = sg.send(message)
    if response.status_code >= 200 and response.status_code < 300:
        st.success("New session added and notification email sent successfully!")
    else:
        st.error(f"Session saved but email failed to send. Status Code: {response.status_code}")
except Exception as e:
    st.error(f"Session saved but email failed to send: {e}")
