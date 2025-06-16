import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import Session, InstructionSession, InstructionSessionSLO
from librarians import librarian_list
from campuses import campus_list
from sqlalchemy.orm import joinedload

def parse_date(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None

def load_sessions():
    db_session = Session()
    sessions = db_session.query(InstructionSession).options(joinedload(InstructionSession.slos)).all()
    db_session.close()
    return sessions

def cancel_session(session_id):
    db_session = Session()
    session_to_cancel = db_session.query(InstructionSession).filter_by(id=session_id).first()
    if session_to_cancel:
        session_to_cancel.canceled = True
        session_to_cancel.canceled_reason = "Canceled via interface"
        db_session.commit()
    db_session.close()

st.title("Edit Instruction Sessions")

# Handle cancel requests via query parameters
cancel_session_id = st.query_params.get('cancel_session_id')
if cancel_session_id:
    cancel_session(int(cancel_session_id))
    st.query_params.clear()  # Clear the URL parameters after handling
    st.rerun()

all_sessions = load_sessions()

request_columns = [
    'ID', 'Date Requested 1', 'Date Confirmed', 'First', 'Last', 'Campus',
    'Librarian', 'Course Code', 'Course_Number', 'Type', 'SLOs'
]

confirmed_columns = [
    'ID', 'Date Confirmed', 'First', 'Last', 'Campus', 'Librarian',
    'Course Code', 'Course_Number', 'Type', 'SLOs', 'Number of Students',
    'Day of Week', 'Campus_Room', 'Assessment'
]

canceled_columns = confirmed_columns + ['Canceled Reason']

if not all_sessions:
    st.warning("No instruction sessions found.")
else:
    data = pd.DataFrame([{
        'ID': s.id,
        'Date Requested 1': s.date_1,
        'Date Confirmed': s.date_of_session,
        'Campus': s.campus,
        'Librarian': s.librarian_presenter,
        'First': s.first,
        'Last': s.last,
        'Course Code': s.course_code,
        'Course_Number': s.course_number,
        'Type': s.type,
        'SLOs': [slo.slo for slo in s.slos],
        'Number of Students': s.number_of_students,
        'Campus_Room': s.campus_room,
        'Assessment': s.assessment,
        'Canceled': getattr(s, 'canceled', False),
        'Canceled Reason': getattr(s, 'canceled_reason', "")
    } for s in all_sessions])

    data['Day of Week'] = data['Date Confirmed'].apply(lambda x: x.strftime('%A') if pd.notna(x) else None)

    campus_names = [campus['name'] for campus in campus_list]
    librarian_names = [lib['name'] for lib in librarian_list]

    campus_options = ["All"] + sorted(campus_names)
    librarian_options = ["All"] + sorted(librarian_names)

    st.sidebar.header("Filter Options")
    selected_campus = st.sidebar.selectbox("Select Campus", campus_options)
    selected_librarian = st.sidebar.selectbox("Select Librarian", librarian_options)

    filtered_data = data.copy()
    if selected_campus != "All":
        filtered_data = filtered_data[filtered_data['Campus'] == selected_campus]
    if selected_librarian != "All":
        filtered_data = filtered_data[filtered_data['Librarian'] == selected_librarian]

    requests_df = filtered_data[(filtered_data['Date Confirmed'].isna()) & (~filtered_data['Canceled'])]
    confirmed_df = filtered_data[(filtered_data['Date Confirmed'].notna()) & (~filtered_data['Canceled'])]
    canceled_df = filtered_data[filtered_data['Canceled']]

    requests_df = requests_df[request_columns]
    confirmed_df = confirmed_df[confirmed_columns]
    canceled_df = canceled_df[canceled_columns]

    column_config_requests = {
        "Campus": st.column_config.SelectboxColumn(label="Campus", options=[""] + sorted(campus_names)),
        "Librarian": st.column_config.SelectboxColumn(label="Librarian", options=[""] + sorted(librarian_names)),
    }

    column_config_confirmed = {
        "Campus": st.column_config.SelectboxColumn(label="Campus", options=[""] + sorted(campus_names)),
        "Librarian": st.column_config.SelectboxColumn(label="Librarian", options=[""] + sorted(librarian_names)),
    }

    # ====================== Requests Section ======================
    st.subheader("Instruction Session Requests (Not Yet Confirmed)")
    for idx, row in requests_df.iterrows():
        cols = st.columns([6, 1, 1])
        with cols[0]:
            single_row_df = pd.DataFrame([row])
            edited_row = st.data_editor(
                single_row_df,
                disabled=['ID', 'Date Requested 1', 'First', 'Last', 'Course Code', 'Course_Number', 'Type', 'SLOs'],
                column_config=column_config_requests,
                key=f'request_editor_{row["ID"]}'
            )
        with cols[1]:
            if st.button("Save", key=f"save_request_{row['ID']}"):
                db_session = Session()
                session_to_update = db_session.query(InstructionSession).filter_by(id=row['ID']).first()
                if session_to_update:
                    session_to_update.campus = edited_row.iloc[0]['Campus']
                    session_to_update.librarian_presenter = edited_row.iloc[0]['Librarian']
                    session_to_update.date_of_session = parse_date(edited_row.iloc[0]['Date Confirmed'])
                    db_session.commit()
                db_session.close()
                st.success(f"Request {row['ID']} updated.")
                st.rerun()
        with cols[2]:
            if st.button("Cancel", key=f"cancel_request_{row['ID']}"):
                st.query_params["cancel_session_id"] = row['ID']
                st.rerun()

    # ====================== Confirmed Section ======================
    st.subheader("Confirmed Instruction Sessions")
    for idx, row in confirmed_df.iterrows():
        cols = st.columns([6, 1])
        with cols[0]:
            single_row_df = pd.DataFrame([row])
            edited_row = st.data_editor(
                single_row_df,
                disabled=['ID', 'First', 'Last', 'Campus', 'Type', 'Course Code', 'Course_Number', 'SLOs', 'Day of Week'],
                column_config=column_config_confirmed,
                key=f'confirmed_editor_{row["ID"]}'
            )
        with cols[1]:
            if st.button("Cancel", key=f"cancel_{row['ID']}"):
                st.query_params["cancel_session_id"] = row['ID']
                st.rerun()

    # ====================== Canceled Section ======================
    st.subheader("Canceled Instruction Sessions")
    if canceled_df.empty:
        st.write("No canceled sessions.")
    else:
        st.data_editor(canceled_df, disabled=True, key='canceled_sessions')
