import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from database import Base, engine

# Connect to SQLite DB
engine = create_engine("sqlite:///acc_library_il.db")

st.title("Library Instruction Dashboard")

# Read table into DataFrame
df = pd.read_sql_table('instruction_sessions', con=engine)

# Fix: Use 'canceled' boolean (1 = True, 0 = False)
canceled_df = df[df['canceled'] == 1]
confirmed_df = df[(df['canceled'] == 0) | (df['canceled'].isna())]  # show NaN as not canceled


# Display full confirmed session data
st.subheader("All Confirmed Instruction Sessions")
st.dataframe(confirmed_df)

# Sessions by Campus
st.subheader("Total Confirmed Sessions by Campus")
campus_counts = confirmed_df['campus'].value_counts().reset_index()
campus_counts.columns = ['Campus', 'Total Sessions']
st.dataframe(campus_counts)

# Sessions by Librarian
st.subheader("Total Confirmed Sessions by Librarian")
librarian_counts = confirmed_df['librarian_presenter'].value_counts().reset_index()
librarian_counts.columns = ['Librarian', 'Total Sessions']
st.dataframe(librarian_counts)

# Librarian Instruction Session Breakdown by Type
st.subheader("Librarian Instruction Session Breakdown by Type")
type_counts = confirmed_df.groupby(['librarian_presenter', 'type']).size().unstack(fill_value=0)

for expected_type in ['In-Person', 'Asynchronous', 'Synchronous']:
    if expected_type not in type_counts.columns:
        type_counts[expected_type] = 0

type_counts['Total'] = type_counts['In-Person'] + type_counts['Asynchronous'] + type_counts['Synchronous']
type_counts = type_counts.reset_index().rename(columns={'librarian_presenter': 'Librarian'})
st.dataframe(type_counts)

# Total Sessions by Month
st.subheader("Total Confirmed Sessions by Month")
confirmed_df['date_of_session'] = pd.to_datetime(confirmed_df['date_of_session'], errors='coerce')
df_month = confirmed_df.dropna(subset=['date_of_session'])
df_month['Month'] = df_month['date_of_session'].dt.strftime('%B %Y')

month_counts = df_month['Month'].value_counts().reset_index()
month_counts.columns = ['Month', 'Total Sessions']
month_counts['SortDate'] = pd.to_datetime(month_counts['Month'], format='%B %Y')
month_counts = month_counts.sort_values('SortDate').drop(columns=['SortDate'])

ytd_total = month_counts['Total Sessions'].sum()
ytd_row = pd.DataFrame([{'Month': 'Year to Date (YTD)', 'Total Sessions': ytd_total}])
month_counts = pd.concat([month_counts, ytd_row], ignore_index=True)

st.dataframe(month_counts)

# Show total canceled session count
st.subheader("Canceled Sessions")
st.write(f"Total Canceled Sessions: {len(canceled_df)}")
st.dataframe(canceled_df)  # optional: show canceled session details
