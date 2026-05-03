import streamlit as st
from datetime import datetime, timedelta
from services.session import require_auth, sidebar_nav
from services.firebase import get_db
from services.ai_service import generate_daily_tasks

st.set_page_config(page_title="Tasks", page_icon="✅", layout="wide")

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

st.title("✅ Today's Tasks")
st.caption(today)

DIFF_COLOR = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
TYPE_ICON = {"reading": "📖", "video": "🎥", "practice": "💻", "revision": "🔄"}

def load_tasks():
    docs = list(db.collection("tasks").where("userId", "==", uid).where("date", "==", today).limit(1).stream())
    return (docs[0].reference, docs[0].to_dict().get("tasks", [])) if docs else (None, [])

def save_tasks(ref, tasks):
    ref.update({"tasks": tasks})
    # Update progress
    total = len(tasks)
    done = sum(1 for t in tasks if t.get("completed"))
    completion = round((done / total) * 100) if total > 0 else 0
    prog_docs = list(db.collection("progress").where("userId", "==", uid).where("date", "==", today).limit(1).stream())
    if prog_docs:
        prog_docs[0].reference.update({"task_completion": completion, "daily_score": completion})
    else:
        db.collection("progress").add({"userId": uid, "date": today, "task_completion": completion, "daily_score": completion})

col1, col2 = st.columns([3, 1])
with col2:
    if st.button("✨ Generate Tasks", use_container_width=True):
        plan_docs = list(db.collection("plans").where("userId", "==", uid).limit(1).stream())
        if not plan_docs:
            st.error("No plan found. Create a plan first.")
        else:
            plan = plan_docs[0].to_dict()
            with st.spinner("Generating tasks..."):
                try:
                    # Carry over incomplete tasks from yesterday
                    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                    y_docs = list(db.collection("tasks").where("userId", "==", uid).where("date", "==", yesterday).limit(1).stream())
                    carry = []
                    if y_docs:
                        carry = [dict(t, carriedOver=True) for t in y_docs[0].to_dict().get("tasks", []) if not t.get("completed")]

                    new_tasks = generate_daily_tasks(plan["topic"], plan["level"], plan["daily_time_hours"], today)
                    all_tasks = carry + new_tasks

                    existing = list(db.collection("tasks").where("userId", "==", uid).where("date", "==", today).limit(1).stream())
                    if existing:
                        existing[0].reference.set({"userId": uid, "date": today, "tasks": all_tasks}, merge=True)
                    else:
                        db.collection("tasks").add({"userId": uid, "date": today, "tasks": all_tasks})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

ref, tasks = load_tasks()

if not tasks:
    st.info("No tasks for today. Click 'Generate Tasks' to get started.")
    st.stop()

done = sum(1 for t in tasks if t.get("completed"))
total = len(tasks)
pct = round((done / total) * 100) if total > 0 else 0

st.progress(pct / 100, text=f"{done}/{total} tasks completed ({pct}%)")
st.divider()

updated = False
for i, task in enumerate(tasks):
    col_check, col_info = st.columns([0.05, 0.95])
    with col_check:
        checked = st.checkbox("", value=task.get("completed", False), key=f"task_{i}", label_visibility="collapsed")
        if checked != task.get("completed"):
            tasks[i]["completed"] = checked
            updated = True
    with col_info:
        title_style = f"~~{task['title']}~~" if task.get("completed") else f"**{task['title']}**"
        carry_badge = " `carried over`" if task.get("carriedOver") else ""
        diff = DIFF_COLOR.get(task.get("difficulty", ""), "⚪")
        icon = TYPE_ICON.get(task.get("type", ""), "📌")
        st.markdown(f"{icon} {title_style}{carry_badge}")
        st.caption(f"{task.get('description', '')}  ·  ⏱ {task.get('estimatedTime', '')}  ·  {diff} {task.get('difficulty', '')}")

if updated and ref:
    save_tasks(ref, tasks)
    st.rerun()
