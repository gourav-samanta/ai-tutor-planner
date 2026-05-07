import streamlit as st
from datetime import datetime, timedelta
from services.session import require_auth, sidebar_nav
from services.firebase import get_db
from services.ai_service import generate_daily_tasks, generate_task_learning_content

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

# Check if a plan is selected
from services.session import get_active_plan_id
active_plan_id = get_active_plan_id()
if not active_plan_id:
    st.warning("⚠️ No subject selected. Please select a subject from the Library or create a new plan.")
    st.stop()

st.title("✅ Today's Tasks")
st.caption(today)

DIFF_COLOR = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
TYPE_ICON = {"reading": "📖", "video": "🎥", "practice": "💻", "revision": "🔄"}

def load_tasks():
    from services.session import get_active_plan_id
    active_plan_id = get_active_plan_id()
    if not active_plan_id:
        return (None, [])
    docs = list(db.collection("tasks")
        .where("userId", "==", uid)
        .where("planId", "==", active_plan_id)
        .where("date", "==", today)
        .limit(1).stream())
    return (docs[0].reference, docs[0].to_dict().get("tasks", [])) if docs else (None, [])

def save_tasks(ref, tasks):
    ref.update({"tasks": tasks})
    # Update progress
    total = len(tasks)
    done = sum(1 for t in tasks if t.get("completed"))
    completion = round((done / total) * 100) if total > 0 else 0
    
    from services.session import get_active_plan_id
    active_plan_id = get_active_plan_id()
    
    prog_docs = list(db.collection("progress")
        .where("userId", "==", uid)
        .where("planId", "==", active_plan_id)
        .where("date", "==", today)
        .limit(1).stream())
    if prog_docs:
        prog_docs[0].reference.update({"task_completion": completion, "daily_score": completion})
    else:
        db.collection("progress").add({
            "userId": uid,
            "planId": active_plan_id,
            "date": today,
            "task_completion": completion,
            "daily_score": completion
        })

def auto_generate_tasks():
    """Auto-generate tasks if not already generated today"""
    from services.session import get_active_plan_id
    
    active_plan_id = get_active_plan_id()
    if not active_plan_id:
        return False
    
    # Get the active plan
    plan_doc = db.collection("plans").document(active_plan_id).get()
    if not plan_doc.exists:
        return False
    
    plan = plan_doc.to_dict()
    
    try:
        # Carry over incomplete tasks from yesterday
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        y_docs = list(db.collection("tasks")
            .where("userId", "==", uid)
            .where("planId", "==", active_plan_id)
            .where("date", "==", yesterday)
            .limit(1).stream())
        carry = []
        if y_docs:
            carry = [dict(t, carriedOver=True) for t in y_docs[0].to_dict().get("tasks", []) if not t.get("completed")]

        new_tasks = generate_daily_tasks(plan["topic"], plan["level"], plan["daily_time_hours"], today)
        all_tasks = carry + new_tasks

        existing = list(db.collection("tasks")
            .where("userId", "==", uid)
            .where("planId", "==", active_plan_id)
            .where("date", "==", today)
            .limit(1).stream())
        if existing:
            existing[0].reference.set({"userId": uid, "planId": active_plan_id, "date": today, "tasks": all_tasks}, merge=True)
        else:
            db.collection("tasks").add({"userId": uid, "planId": active_plan_id, "date": today, "tasks": all_tasks})
        return True
    except Exception as e:
        st.error(f"Error generating tasks: {e}")
        return False

# Auto-generate tasks if they don't exist for today
ref, tasks = load_tasks()
if not tasks:
    with st.spinner("🔄 Generating today's tasks..."):
        if auto_generate_tasks():
            st.success("✅ Tasks generated successfully!")
            st.rerun()
        else:
            st.warning("⚠️ No learning plan found. Please create a plan first using the AI Planner.")
            st.stop()

# Get plan details for learning content generation
plan_doc = db.collection("plans").document(active_plan_id).get()
plan = plan_doc.to_dict() if plan_doc.exists else {}

# Display task completion progress

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
        
        # Learn More button
        if st.button(f"📚 Learn More", key=f"learn_{i}", use_container_width=False):
            with st.spinner("🤔 Generating learning content..."):
                try:
                    content = generate_task_learning_content(
                        task['title'],
                        task.get('description', ''),
                        plan.get('topic', 'this topic'),
                        plan.get('level', 'beginner')
                    )
                    st.session_state[f"learn_content_{i}"] = content
                except Exception as e:
                    st.session_state[f"learn_content_{i}"] = f"⚠️ Error: {str(e)}"
        
        # Display learning content if available
        if f"learn_content_{i}" in st.session_state:
            with st.expander("📖 Learning Content", expanded=True):
                st.markdown(st.session_state[f"learn_content_{i}"])
                if st.button("✖️ Close", key=f"close_{i}"):
                    del st.session_state[f"learn_content_{i}"]
                    st.rerun()
    
    st.divider()

if updated and ref:
    save_tasks(ref, tasks)
    st.rerun()
