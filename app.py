import streamlit as st
from services.auth_service import login, signup

st.set_page_config(page_title="AI Tutor Planner", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

# Hide default Streamlit navigation
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

def auth_page():
    st.title("🎓 AI Tutor Planner")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                try:
                    user = login(email, password)
                    st.session_state.user = user
                    st.success("Logged in!")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    with tab2:
        with st.form("signup_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email", key="su_email")
            password = st.text_input("Password", type="password", key="su_pass")
            submitted = st.form_submit_button("Sign Up", use_container_width=True)
            if submitted:
                try:
                    user = signup(name, email, password)
                    st.session_state.user = user
                    st.success("Account created!")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

# Auth gate
if "user" not in st.session_state or not st.session_state.user:
    auth_page()
    st.stop()

# Redirect to New Plan page (chatbot)
st.switch_page("pages/2_Input.py")
