import streamlit as st
from services.auth_service import login, signup

st.set_page_config(page_title="AI Tutor Planner", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

# Hide default Streamlit navigation
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
    section[data-testid="stSidebar"] {display: none;}
    .main {
        max-width: 600px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

def auth_page():
    # Hero section
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0 1.5rem 0;'>
            <div style='font-size: 3rem; margin-bottom: 0.5rem;'>🎓</div>
            <h1 style='font-size: 2.5rem; font-weight: 700; 
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       margin-bottom: 0.5rem;'>
                AI Tutor Planner
            </h1>
            <p style='font-size: 1rem; color: #94a3b8; max-width: 400px; margin: 0 auto;'>
                Your personal AI-powered learning companion
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "✨ Create Account"])

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
