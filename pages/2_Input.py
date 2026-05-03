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

# Initialize conversation state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "Hi! I'm your AI Learning Planner. Let's create a personalized learning plan for you.\n\n**What would you like to learn?** (e.g., Python programming, Digital Marketing, Machine Learning)"}]

if "plan_info" not in st.session_state:
    st.session_state.plan_info = {}

if "conversation_stage" not in st.session_state:
    st.session_state.conversation_stage = "topic"  # topic -> duration -> level -> confirm

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
user_input = st.chat_input("Type your response here...")
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    stage = st.session_state.conversation_stage
    
    # Process based on conversation stage
    if stage == "topic":
        st.session_state.plan_info["topic"] = user_input
        reply = f"Great! You want to learn **{user_input}**.\n\n**How much time do you have?** (e.g., 2 weeks, 1 month, 3 months)"
        st.session_state.conversation_stage = "duration"
        
    elif stage == "duration":
        st.session_state.plan_info["duration"] = user_input
        reply = f"Perfect! You have **{user_input}** to learn.\n\n**What's your current experience level?**\n- Beginner (just starting)\n- Intermediate (some experience)\n- Advanced (experienced)"
        st.session_state.conversation_stage = "level"
        
    elif stage == "level":
        # Parse level
        level_input = user_input.lower()
        if "beginner" in level_input or "start" in level_input or "new" in level_input:
            level = "beginner"
        elif "advanced" in level_input or "expert" in level_input or "experienced" in level_input:
            level = "advanced"
        else:
            level = "intermediate"
        
        st.session_state.plan_info["level"] = level
        
        # Show summary and ask for confirmation
        topic = st.session_state.plan_info["topic"]
        duration = st.session_state.plan_info["duration"]
        
        reply = f"Awesome! Here's what I have:\n\n📚 **Topic:** {topic}\n⏱️ **Duration:** {duration}\n📊 **Level:** {level}\n\n**Would you like to:**\n1. Create the plan now with these details\n2. Fill a detailed form for more customization\n\nType '1' to create now or '2' for the form."
        st.session_state.conversation_stage = "confirm"
        
    elif stage == "confirm":
        if "1" in user_input or "create" in user_input.lower() or "now" in user_input.lower():
            # Create plan with collected info
            with st.spinner("Creating your personalized learning plan..."):
                try:
                    topic = st.session_state.plan_info["topic"]
                    duration = st.session_state.plan_info["duration"]
                    level = st.session_state.plan_info["level"]
                    
                    roadmap = generate_roadmap(topic, "skill learning", duration, 2, level)
                    plan_data = {
                        "userId": uid,
                        "purpose": "skill learning",
                        "topic": topic,
                        "duration": duration,
                        "daily_time_hours": 2,
                        "level": level,
                        "roadmap": roadmap
                    }
                    
                    # Save to database
                    existing = list(db.collection("plans").where("userId", "==", uid).limit(1).stream())
                    if existing:
                        existing[0].reference.set(plan_data, merge=True)
                    else:
                        db.collection("plans").add(plan_data)

                    reply = f"✅ **Your learning plan is ready!**\n\nI've created a personalized roadmap for **{topic}** over **{duration}** at **{level}** level.\n\n🗺️ View your **Roadmap** to see the weekly breakdown\n✅ Check **Tasks** for daily activities\n📝 Take **Tests** to assess your progress\n📈 Track your **Progress** over time\n\nGood luck with your learning journey! 🚀"
                    st.session_state["plan"] = plan_data
                    
                    # Reset conversation
                    st.session_state.conversation_stage = "topic"
                    st.session_state.plan_info = {}
                    
                except Exception as e:
                    reply = f"❌ Sorry, something went wrong: {e}\n\nLet's try again. What would you like to learn?"
                    st.session_state.conversation_stage = "topic"
                    st.session_state.plan_info = {}
                    
        elif "2" in user_input or "form" in user_input.lower() or "detail" in user_input.lower():
            # Show detailed form
            reply = "Great! Let me show you the detailed form below. Fill it out and click 'Generate Plan'."
            st.session_state.conversation_stage = "form"
        else:
            reply = "Please type '1' to create the plan now or '2' to use the detailed form."
    
    else:
        reply = "Let's start over. What would you like to learn?"
        st.session_state.conversation_stage = "topic"
        st.session_state.plan_info = {}
    
    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
    
    st.rerun()

# Show form if user chose detailed form option
if st.session_state.get("conversation_stage") == "form":
    st.divider()
    st.subheader("📋 Detailed Learning Plan Form")
    
    with st.form("detailed_plan_form"):
        col1, col2 = st.columns(2)
        with col1:
            purpose = st.selectbox("Purpose", ["skill learning", "job preparation", "academic", "other"])
            topic = st.text_input("Topic", value=st.session_state.plan_info.get("topic", ""), placeholder="e.g. Python for Data Science")
            duration = st.text_input("Duration", value=st.session_state.plan_info.get("duration", ""), placeholder="e.g. 4 weeks, 2 months")
        with col2:
            daily_hours = st.slider("Daily Time (hours)", 1, 8, 2)
            level = st.select_slider("Skill Level", options=["beginner", "intermediate", "advanced"], value=st.session_state.plan_info.get("level", "beginner"))

        submitted = st.form_submit_button("🚀 Generate My Plan", use_container_width=True)

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
                    
                    existing = list(db.collection("plans").where("userId", "==", uid).limit(1).stream())
                    if existing:
                        existing[0].reference.set(plan_data, merge=True)
                    else:
                        db.collection("plans").add(plan_data)

                    st.success("✅ Your learning plan is ready! Check the Roadmap page.")
                    st.session_state["plan"] = plan_data
                    
                    # Add to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": f"✅ Plan created successfully for **{topic}**! View it in the Roadmap section."})
                    
                    # Reset conversation
                    st.session_state.conversation_stage = "topic"
                    st.session_state.plan_info = {}
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {e}")
