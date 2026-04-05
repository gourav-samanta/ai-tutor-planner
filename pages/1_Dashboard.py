import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from services.session import require_auth, sidebar_nav
from services.firebase import get_db

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
sidebar_nav()
user = require_auth()
db = get_db()
uid = user["uid"]
today = datetime.now().strftime("%Y-%m-%d")

st.title("📊 Dashboard")
st.caption(datetime.now().strftime("%A, %B %d %Y"))

# Fetch today's tasks
task_docs = db.collection("tasks").where("userId", "==", uid).where("date", "==", today).limit(1).stream()
tasks = []
for doc in task_docs:
    tasks = doc.to_dict().get("tasks", [])

done = sum(1 for t in tasks if t.get("completed"))
total = len(tasks)
pct = round((done / total) * 100) if total > 0 else 0

# Fetch weekly progress
week_start = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
prog_docs = db.collection("progress").where("userId", "==", uid).where("date", ">=", week_start).stream()
records = [d.to_dict() for d in prog_docs]
records.sort(key=lambda x: x["date"])

avg_score = round(sum(r.get("daily_score", 0) for r in records) / len(records)) if records else 0
streak = sum(1 for r in records if r.get("daily_score", 0) >= 50)

# Stats row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Today's Tasks", f"{done}/{total}")
col2.metric("Completion", f"{pct}%")
col3.metric("Avg Score (7d)", f"{avg_score}%")
col4.metric("🔥 Streak", f"{streak} days")

st.divider()
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Today's Tasks")
    if not tasks:
        st.info("No tasks yet. Go to Tasks page to generate them.")
    else:
        st.progress(pct / 100)
        for t in tasks[:5]:
            icon = "✅" if t.get("completed") else "⬜"
            label = f"~~{t['title']}~~" if t.get("completed") else t["title"]
            st.markdown(f"{icon} {label}")

with col_right:
    st.subheader("Weekly Performance")
    if records:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[r["date"][5:] for r in records],
            y=[r.get("daily_score", 0) for r in records],
            mode="lines+markers", fill="tozeroy",
            line=dict(color="#6366f1", width=2),
            marker=dict(size=6)
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[0, 100], gridcolor="#1f2937", color="#9ca3af"),
            xaxis=dict(gridcolor="#1f2937", color="#9ca3af"),
            margin=dict(l=0, r=0, t=10, b=0), height=220
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No performance data yet.")

st.divider()
st.subheader("Quick Actions")
q1, q2, q3, q4 = st.columns(4)
if q1.button("🎯 New Plan", use_container_width=True):
    st.switch_page("pages/2_Input.py")
if q2.button("🗺️ Roadmap", use_container_width=True):
    st.switch_page("pages/3_Roadmap.py")
if q3.button("📝 Take Test", use_container_width=True):
    st.switch_page("pages/5_Tests.py")
if q4.button("📈 Progress", use_container_width=True):
    st.switch_page("pages/6_Progress.py")
