import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Connect to your custom SQLite DB
engine = create_engine("sqlite:///acc_library_il.db")

st.title("Library Instruction Dashboard")

# Read full table into DataFrame
df = pd.read_sql_table('instruction_sessions', con=engine)

# Display full session data
st.subheader("All Instruction Sessions")
st.dataframe(df)

# Sessions by Campus
st.subheader("Total Sessions by Campus")
campus_counts = df['campus'].value_counts().reset_index()
campus_counts.columns = ['Campus', 'Total Sessions']
st.dataframe(campus_counts)

# Sessions by Librarian
st.subheader("Total Sessions by Librarian")
librarian_counts = df['librarian_presenter'].value_counts().reset_index()
librarian_counts.columns = ['Librarian', 'Total Sessions']
st.dataframe(librarian_counts)

# Detailed breakdown by Librarian and Type
st.subheader("Librarian Instruction Session Breakdown by Type")

type_counts = df.groupby(['librarian_presenter', 'type']).size().unstack(fill_value=0)

# Ensure expected type columns are present
for expected_type in ['In-Person', 'Asynchronous', 'Synchronous']:
    if expected_type not in type_counts.columns:
        type_counts[expected_type] = 0

type_counts['Total'] = type_counts['In-Person'] + type_counts['Asynchronous'] + type_counts['Synchronous']
type_counts = type_counts.reset_index().rename(columns={'librarian_presenter': 'Librarian'})
st.dataframe(type_counts)

# Total Sessions by Month
st.subheader("Total Sessions by Month")

# Convert 'date_of_session' to datetime
df['date_of_session'] = pd.to_datetime(df['date_of_session'], errors='coerce')

# Drop rows where 'date_of_session' is NaT
df_month = df.dropna(subset=['date_of_session'])

# Extract Month Name and Year
df_month['Month'] = df_month['date_of_session'].dt.strftime('%B %Y')  # Example: 'June 2025'

# Count sessions per Month
month_counts = df_month['Month'].value_counts().reset_index()
month_counts.columns = ['Month', 'Total Sessions']

# Sort by datetime to ensure proper order
month_counts['SortDate'] = pd.to_datetime(month_counts['Month'], format='%B %Y')
month_counts = month_counts.sort_values('SortDate').drop(columns=['SortDate'])

# Calculate Year-To-Date Total
ytd_total = month_counts['Total Sessions'].sum()

# Append YTD row
ytd_row = pd.DataFrame([{'Month': 'Year to Date (YTD)', 'Total Sessions': ytd_total}])
month_counts = pd.concat([month_counts, ytd_row], ignore_index=True)

st.dataframe(month_counts)
