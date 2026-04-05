import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
from services.session import require_auth, sidebar_nav
from services.firebase import get_db
from services.ai_service import generate_ai_summary

st.set_page_config(page_title="Progress", page_icon="📈", layout="wide")
sidebar_nav()
user = require_auth()
db = get_db()
uid = user["uid"]

st.title("📈 Performance Tracker")

range_opt = st.radio("Range", ["Weekly", "Monthly"], horizontal=True)
st.divider()

now = datetime.now()
if range_opt == "Monthly":
    start = datetime(now.year, now.month, 1).strftime("%Y-%m-%d")
else:
    start = (now - timedelta(days=6)).strftime("%Y-%m-%d")
end = now.strftime("%Y-%m-%d")

docs = list(db.collection("progress").where("userId", "==", uid).where("date", ">=", start).where("date", "<=", end).stream())
records = sorted([d.to_dict() for d in docs], key=lambda x: x["date"])

# Line chart
st.subheader("Performance Graph")
if records:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[r["date"][5:] for r in records],
        y=[r.get("task_completion", 0) for r in records],
        name="Task Completion %", mode="lines+markers", fill="tozeroy",
        line=dict(color="#6366f1", width=2)
    ))
    fig.add_trace(go.Scatter(
        x=[r["date"][5:] for r in records],
        y=[r.get("test_score") or 0 for r in records],
        name="Test Score %", mode="lines+markers", fill="tozeroy",
        line=dict(color="#8b5cf6", width=2)
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, 100], gridcolor="#1f2937", color="#9ca3af"),
        xaxis=dict(gridcolor="#1f2937", color="#9ca3af"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#9ca3af")),
        margin=dict(l=0, r=0, t=10, b=0), height=300
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data yet. Complete tasks and tests to see your progress.")

# AI Summary
if records:
    with st.expander("🤖 AI Performance Summary", expanded=True):
        with st.spinner("Generating summary..."):
            summary = generate_ai_summary(records)
        st.write(summary)

st.divider()

# Monthly calendar
if range_opt == "Monthly":
    st.subheader("Monthly Calendar")
    score_map = {r["date"]: r.get("daily_score", 0) for r in records}
    days_in_month = calendar.monthrange(now.year, now.month)[1]

    monthly_score = round(sum(score_map.values()) / len(score_map)) if score_map else None
    if monthly_score is not None:
        st.metric("Monthly Score", f"{monthly_score}/100")

    # Build calendar grid
    first_weekday = calendar.monthrange(now.year, now.month)[0]  # 0=Mon
    cols = st.columns(7)
    days_header = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, d in enumerate(days_header):
        cols[i].markdown(f"<center><small>{d}</small></center>", unsafe_allow_html=True)

    day_num = 1
    cells = [""] * first_weekday + list(range(1, days_in_month + 1))
    # Pad to full weeks
    while len(cells) % 7 != 0:
        cells.append("")

    for week_start in range(0, len(cells), 7):
        week = cells[week_start:week_start + 7]
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == "":
                cols[i].markdown(" ")
            else:
                date_str = f"{now.year}-{str(now.month).zfill(2)}-{str(day).zfill(2)}"
                score = score_map.get(date_str)
                if score is None:
                    color = "#1f2937"
                    text_color = "#6b7280"
                elif score >= 70:
                    color = "#06b6d4"
                    text_color = "#000"
                elif score >= 40:
                    color = "#eab308"
                    text_color = "#000"
                else:
                    color = "#ef4444"
                    text_color = "#fff"
                cols[i].markdown(
                    f'<div style="background:{color};color:{text_color};border-radius:6px;text-align:center;padding:6px 0;font-size:13px;font-weight:500">{day}</div>',
                    unsafe_allow_html=True
                )

    st.markdown("")
    st.markdown("🟦 Good (≥70%)  &nbsp; 🟨 Average (40-69%)  &nbsp; 🟥 Bad (<40%)  &nbsp; ⬛ No data")
