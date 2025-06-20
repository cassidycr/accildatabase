import streamlit as st

st.set_page_config(
    page_title="Library Instruction App",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar content
st.sidebar.title("📚 ACC Library Instruction")
st.sidebar.markdown("---")  # horizontal divider
st.sidebar.markdown("### Navigation appears below ⬇️")
st.sidebar.info("Use this sidebar to navigate to Dashboard, Instruction Form, or Sessions.")

# Main page content
st.title("Library Instruction App")
st.write("Welcome to the ACC Library Instruction Database App!")
st.write("Use the sidebar to select a page.")
