import streamlit as st
import pandas as pd
from services.session import require_auth, sidebar_nav
from services.firebase import get_db

st.set_page_config(page_title="Roadmap", page_icon="🗺️", layout="wide")

# Hide default Streamlit navigation
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

sidebar_nav()
user = require_auth()
db = get_db()
uid = user["uid"]

st.title("🗺️ Learning Roadmap")

# Load plan
docs = list(db.collection("plans").where("userId", "==", uid).limit(1).stream())
if not docs:
    st.warning("No roadmap found.")
    if st.button("Create a Plan"):
        st.switch_page("pages/2_Input.py")
    st.stop()

plan = docs[0].to_dict()

st.markdown(f"**Topic:** {plan['topic']} &nbsp;|&nbsp; **Level:** {plan['level']} &nbsp;|&nbsp; **Duration:** {plan['duration']} &nbsp;|&nbsp; **Daily:** {plan['daily_time_hours']}h")
st.divider()

roadmap = plan.get("roadmap", [])
if not roadmap:
    st.info("Roadmap is empty.")
    st.stop()

# Build table
rows = []
for week in roadmap:
    rows.append({
        "Week": f"W{week.get('week', '')}",
        "Title": week.get("title", ""),
        "Topics": ", ".join(week.get("topics", [])),
        "Key Concepts": ", ".join(week.get("keyConcepts", [])),
        "Expected Outcome": week.get("expectedOutcome", "")
    })

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True, hide_index=True,
    column_config={
        "Week": st.column_config.TextColumn(width="small"),
        "Title": st.column_config.TextColumn(width="medium"),
        "Topics": st.column_config.TextColumn(width="large"),
        "Key Concepts": st.column_config.TextColumn(width="large"),
        "Expected Outcome": st.column_config.TextColumn(width="large"),
    }
)

st.divider()
if st.button("📋 Go to Today's Tasks", use_container_width=False):
    st.switch_page("pages/4_Tasks.py")
