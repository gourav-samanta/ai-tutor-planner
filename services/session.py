import streamlit as st

def require_auth():
    """Redirect to home/login if not authenticated."""
    if "user" not in st.session_state or not st.session_state.user:
        st.warning("Please login first.")
        st.page_link("app.py", label="Go to Login")
        st.stop()
    return st.session_state.user

def sidebar_nav():
    with st.sidebar:
        user = st.session_state.get("user", {})
        st.markdown("### 🎓 AI Tutor Planner")
        st.markdown(f"👤 **{user.get('name', '')}**")
        st.divider()
        st.page_link("app.py", label="🏠 Home")
        st.page_link("pages/1_Dashboard.py", label="📊 Dashboard")
        st.page_link("pages/2_Input.py", label="🎯 New Plan")
        st.page_link("pages/3_Roadmap.py", label="🗺️ Roadmap")
        st.page_link("pages/4_Tasks.py", label="✅ Tasks")
        st.page_link("pages/5_Tests.py", label="📝 Tests")
        st.page_link("pages/6_Progress.py", label="📈 Progress")
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
