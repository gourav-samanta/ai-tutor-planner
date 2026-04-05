import streamlit as st
from services.session import require_auth, sidebar_nav
from services.firebase import get_db
from services.ai_service import generate_roadmap

st.set_page_config(page_title="New Plan", page_icon="🎯", layout="wide")
sidebar_nav()
user = require_auth()
db = get_db()
uid = user["uid"]

st.title("🎯 Create Your Learning Plan")

mode = st.radio("Input mode", ["📋 Form", "💬 Chat"], horizontal=True)

if mode == "📋 Form":
    with st.form("plan_form"):
        col1, col2 = st.columns(2)
        with col1:
            purpose = st.selectbox("Purpose", ["job preparation", "skill learning", "academic", "other"])
            topic = st.text_input("Topic", placeholder="e.g. Python for Data Science")
            duration = st.text_input("Duration", placeholder="e.g. 4 weeks, 2 months")
        with col2:
            daily_hours = st.slider("Daily Time (hours)", 1, 8, 2)
            level = st.select_slider("Skill Level", options=["beginner", "intermediate", "advanced"])

        submitted = st.form_submit_button("🚀 Generate My Roadmap", use_container_width=True)

    if submitted:
        if not topic or not duration:
            st.error("Please fill in Topic and Duration.")
        else:
            with st.spinner("Generating your personalized roadmap..."):
                try:
                    roadmap = generate_roadmap(topic, purpose, duration, daily_hours, level)
                    plan_data = {
                        "userId": uid, "purpose": purpose, "topic": topic,
                        "duration": duration, "daily_time_hours": daily_hours,
                        "level": level, "roadmap": roadmap
                    }
                    # Upsert plan
                    existing = list(db.collection("plans").where("userId", "==", uid).limit(1).stream())
                    if existing:
                        existing[0].reference.set(plan_data, merge=True)
                    else:
                        db.collection("plans").add(plan_data)

                    st.success("Roadmap generated!")
                    st.session_state["plan"] = plan_data
                    st.switch_page("pages/3_Roadmap.py")
                except Exception as e:
                    st.error(f"Error: {e}")

else:
    st.info("Describe what you want to learn and I'll build your plan.")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "content": "Hi! Tell me what you want to learn and I'll build your plan."}]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Tell me what you want to learn...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.spinner("Thinking..."):
            try:
                roadmap = generate_roadmap(user_input, "skill learning", "4 weeks", 2, "beginner")
                plan_data = {
                    "userId": uid, "purpose": "skill learning", "topic": user_input,
                    "duration": "4 weeks", "daily_time_hours": 2, "level": "beginner", "roadmap": roadmap
                }
                existing = list(db.collection("plans").where("userId", "==", uid).limit(1).stream())
                if existing:
                    existing[0].reference.set(plan_data, merge=True)
                else:
                    db.collection("plans").add(plan_data)

                reply = f"Great! I've created a roadmap for **{user_input}**. Head to the Roadmap page to see it."
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.session_state["plan"] = plan_data
                with st.chat_message("assistant"):
                    st.write(reply)
            except Exception as e:
                err = f"Sorry, something went wrong: {e}"
                st.session_state.chat_history.append({"role": "assistant", "content": err})
                with st.chat_message("assistant"):
                    st.write(err)
