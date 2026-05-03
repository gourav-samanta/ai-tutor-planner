import streamlit as st
from services.session import require_auth, sidebar_nav
from services.firebase import get_db
from services.ai_service import generate_roadmap

st.set_page_config(page_title="New Plan", page_icon="🎯", layout="wide")

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

st.title("💬 AI Learning Planner")
st.info("Tell me what you want to learn and I'll create a personalized learning plan for you!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "Hi! Tell me what you want to learn and I'll build your personalized learning plan. You can describe your goals, timeline, and experience level."}]

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Tell me what you want to learn...")
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.spinner("Creating your personalized learning plan..."):
        try:
            # Generate roadmap based on user input
            roadmap = generate_roadmap(user_input, "skill learning", "4 weeks", 2, "beginner")
            plan_data = {
                "userId": uid, "purpose": "skill learning", "topic": user_input,
                "duration": "4 weeks", "daily_time_hours": 2, "level": "beginner", "roadmap": roadmap
            }
            
            # Save to database
            existing = list(db.collection("plans").where("userId", "==", uid).limit(1).stream())
            if existing:
                existing[0].reference.set(plan_data, merge=True)
            else:
                db.collection("plans").add(plan_data)

            reply = f"✅ Perfect! I've created a personalized learning roadmap for **{user_input}**.\n\nYou can view your complete roadmap, daily tasks, and track your progress using the sidebar navigation."
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.session_state["plan"] = plan_data
            
            with st.chat_message("assistant"):
                st.write(reply)
                st.success("Your learning plan is ready! Check the Roadmap page.")
        except Exception as e:
            err = f"Sorry, something went wrong: {e}"
            st.session_state.chat_history.append({"role": "assistant", "content": err})
            with st.chat_message("assistant"):
                st.error(err)
