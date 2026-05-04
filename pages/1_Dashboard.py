import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from services.session import require_auth, sidebar_nav
from services.firebase import get_db

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

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
today = datetime.now().strftime("%Y-%m-%d")

# Check if a plan is selected
from services.session import get_active_plan_id
active_plan_id = get_active_plan_id()
if not active_plan_id:
    st.warning("⚠️ No subject selected. Please select a subject from the Library or create a new plan.")
    st.stop()

st.title("📊 Dashboard")
st.caption(datetime.now().strftime("%A, %B %d %Y"))

# Fetch today's tasks for active plan
task_docs = db.collection("tasks")\
    .where("userId", "==", uid)\
    .where("planId", "==", active_plan_id)\
    .where("date", "==", today)\
    .limit(1).stream()
tasks = []
for doc in task_docs:
    tasks = doc.to_dict().get("tasks", [])

done = sum(1 for t in tasks if t.get("completed"))
total = len(tasks)
pct = round((done / total) * 100) if total > 0 else 0

# Fetch weekly progress for active plan
week_start = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
prog_docs = db.collection("progress")\
    .where("userId", "==", uid)\
    .where("planId", "==", active_plan_id)\
    .where("date", ">=", week_start)\
    .stream()
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

# Activity Calendar (GitHub-style)
st.subheader("📅 Activity Calendar")

# Fetch last 90 days of activity
days_back = 90
start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
activity_docs = db.collection("progress")\
    .where("userId", "==", uid)\
    .where("planId", "==", active_plan_id)\
    .where("date", ">=", start_date)\
    .stream()

activity_data = {d.to_dict()["date"]: d.to_dict().get("daily_score", 0) for d in activity_docs}

# Create calendar grid
def get_color(score):
    if score == 0:
        return "#1f2937"  # Dark gray (no activity)
    elif score < 40:
        return "#ef4444"  # Red (poor)
    elif score < 70:
        return "#f59e0b"  # Orange (average)
    else:
        return "#10b981"  # Green (good)

# Generate calendar HTML
calendar_html = '<div style="display: flex; flex-wrap: wrap; gap: 3px; max-width: 100%;">'
for i in range(days_back, -1, -1):
    date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
    score = activity_data.get(date, 0)
    color = get_color(score)
    tooltip = f"{date}: {score}%" if score > 0 else f"{date}: No activity"
    calendar_html += f'<div title="{tooltip}" style="width: 12px; height: 12px; background-color: {color}; border-radius: 2px;"></div>'
calendar_html += '</div>'

# Legend
calendar_html += '''
<div style="margin-top: 10px; display: flex; align-items: center; gap: 10px; font-size: 12px;">
    <span>Less</span>
    <div style="width: 12px; height: 12px; background-color: #1f2937; border-radius: 2px;"></div>
    <div style="width: 12px; height: 12px; background-color: #ef4444; border-radius: 2px;"></div>
    <div style="width: 12px; height: 12px; background-color: #f59e0b; border-radius: 2px;"></div>
    <div style="width: 12px; height: 12px; background-color: #10b981; border-radius: 2px;"></div>
    <span>More</span>
</div>
'''

st.markdown(calendar_html, unsafe_allow_html=True)

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
