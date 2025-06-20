import streamlit as st
import pandas as pd
from session_utils import load_sessions, parse_date
from librarians import librarian_list
from campuses import campus_list
from collections import Counter

st.title("Library Instruction Dashboard")

# Load all sessions from the database
all_sessions = load_sessions()

if not all_sessions:
    st.warning("No instruction sessions found.")
else:
    # Build DataFrame from session data
    data = pd.DataFrame([{
        'ID': s.id,
        'Date Requested 1': parse_date(s.date_1),
        'Date Confirmed': parse_date(s.date_of_session),
        'Campus': s.campus,
        'Librarian': s.librarian_presenter,
        'First': s.first,
        'Last': s.last,
        'Course Code': s.course_code,
        'Course_Number': s.course_number,
        'Type': s.type,
        'SLOs': [slo.slo for slo in s.slos],  # This is a list
        'Number of Students': s.number_of_students,
        'Campus_Room': s.campus_room,
        'Assessment': s.assessment,
        'Canceled': getattr(s, 'canceled', False),
        'Canceled Reason': getattr(s, 'canceled_reason', "")
    } for s in all_sessions])

    data['Day of Week'] = data['Date Confirmed'].apply(lambda x: x.strftime('%A') if pd.notna(x) else None)

    # --- Unconfirmed Sessions Count ---
    unconfirmed_sessions = data[(data['Date Confirmed'].isna()) & (~data['Canceled'])]
    unconfirmed_count = len(unconfirmed_sessions)

    st.markdown(f"<h3 style='color: red;'>Unconfirmed Sessions = {unconfirmed_count}</h3>", unsafe_allow_html=True)

    # --- Confirmed Sessions ---
    confirmed_df = data[(data['Date Confirmed'].notna()) & (~data['Canceled'])]

    # Dashboard displays below:
    st.subheader("All Confirmed Instruction Sessions")
    st.dataframe(confirmed_df)

    # Total Confirmed Sessions by Campus
    st.subheader("Total Confirmed Sessions by Campus")
    campus_counts = confirmed_df['Campus'].value_counts().reset_index()
    campus_counts.columns = ['Campus', 'Total Confirmed Sessions']
    st.dataframe(campus_counts)

    # Total Confirmed Sessions by Librarian
    st.subheader("Total Confirmed Sessions by Librarian")
    librarian_counts = confirmed_df['Librarian'].value_counts().reset_index()
    librarian_counts.columns = ['Librarian', 'Total Confirmed Sessions']
    st.dataframe(librarian_counts)

    # Librarian Instruction Session Breakdown by Type
    st.subheader("Librarian Instruction Session Breakdown by Type")
    type_counts = confirmed_df.groupby(['Librarian', 'Type']).size().unstack(fill_value=0)

    for expected_type in ['In-Person', 'Asynchronous', 'Synchronous']:
        if expected_type not in type_counts.columns:
            type_counts[expected_type] = 0

    type_counts['Total'] = type_counts['In-Person'] + type_counts['Asynchronous'] + type_counts['Synchronous']
    type_counts = type_counts.reset_index()
    st.dataframe(type_counts)

    # Total Confirmed Sessions by Month
    st.subheader("Total Confirmed Sessions by Month")
    confirmed_df['Date Confirmed'] = pd.to_datetime(confirmed_df['Date Confirmed'], errors='coerce')
    df_month = confirmed_df.dropna(subset=['Date Confirmed'])
    df_month['Month'] = df_month['Date Confirmed'].dt.strftime('%B %Y')

    month_counts = df_month['Month'].value_counts().reset_index()
    month_counts.columns = ['Month', 'Total Confirmed Sessions']
    month_counts['SortDate'] = pd.to_datetime(month_counts['Month'], format='%B %Y')
    month_counts = month_counts.sort_values('SortDate').drop(columns=['SortDate'])

    ytd_total = month_counts['Total Confirmed Sessions'].sum()
    ytd_row = pd.DataFrame([{'Month': 'Year to Date (YTD)', 'Total Confirmed Sessions': ytd_total}])
    month_counts = pd.concat([month_counts, ytd_row], ignore_index=True)

    st.dataframe(month_counts)

    # --- SLO Counts ---
    st.subheader("SLO Counts")

    # Flatten SLO lists into one big list
    slo_list = [slo for sublist in confirmed_df['SLOs'] for slo in sublist]
    slo_counts = Counter(slo_list)

    slo_df = pd.DataFrame(slo_counts.items(), columns=['SLO', 'Count']).sort_values(by='Count', ascending=False)
    st.dataframe(slo_df)
