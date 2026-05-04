import streamlit as st

def require_auth():
    """Redirect to home/login if not authenticated."""
    if "user" not in st.session_state or not st.session_state.user:
        st.warning("Please login first.")
        st.page_link("app.py", label="Go to Login")
        st.stop()
    return st.session_state.user

def get_active_plan_id():
    """Get the currently active plan ID"""
    return st.session_state.get("active_plan_id", None)

def set_active_plan(plan_id):
    """Set the active plan"""
    st.session_state["active_plan_id"] = plan_id

def sidebar_nav():
    from services.firebase import get_db
    
    with st.sidebar:
        user = st.session_state.get("user", {})
        st.markdown("### 🎓 AI Tutor Planner")
        st.markdown(f"👤 **{user.get('name', '')}**")
        st.divider()
        
        # Library Section
        st.markdown("### 📚 My Library")
        
        # Get all plans for this user
        db = get_db()
        uid = user.get("uid")
        if uid:
            plans = list(db.collection("plans").where("userId", "==", uid).stream())
            
            if plans:
                active_plan_id = get_active_plan_id()
                
                # If no active plan, set the first one
                if not active_plan_id and plans:
                    set_active_plan(plans[0].id)
                    active_plan_id = plans[0].id
                
                for plan_doc in plans:
                    plan = plan_doc.to_dict()
                    plan_id = plan_doc.id
                    topic = plan.get("topic", "Untitled")
                    
                    # Show active indicator
                    if plan_id == active_plan_id:
                        icon = "📖"
                        label = f"{icon} **{topic}** (Active)"
                    else:
                        icon = "📕"
                        label = f"{icon} {topic}"
                    
                    if st.button(label, key=f"plan_{plan_id}", use_container_width=True):
                        set_active_plan(plan_id)
                        st.rerun()
            else:
                st.info("No subjects yet. Create your first plan!")
        
        st.divider()
        
        # Navigation
        st.page_link("pages/2_Input.py", label="💬 AI Planner")
        st.page_link("pages/1_Dashboard.py", label="📊 Dashboard")
        st.page_link("pages/3_Roadmap.py", label="🗺️ Roadmap")
        st.page_link("pages/4_Tasks.py", label="✅ Tasks")
        st.page_link("pages/5_Tests.py", label="📝 Tests")
        st.page_link("pages/6_Progress.py", label="📈 Progress")
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
