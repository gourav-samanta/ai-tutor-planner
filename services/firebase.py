import firebase_admin
from firebase_admin import credentials, firestore, auth
import streamlit as st

def init_firebase():
    if not firebase_admin._apps:
        cred_dict = {
            "type": st.secrets["firebase"]["type"],
            "project_id": st.secrets["firebase"]["project_id"],
            "private_key_id": st.secrets["firebase"]["private_key_id"],
            "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),
            "client_email": st.secrets["firebase"]["client_email"],
            "client_id": st.secrets["firebase"]["client_id"],
            "auth_uri": st.secrets["firebase"]["auth_uri"],
            "token_uri": st.secrets["firebase"]["token_uri"],
        }
        cred = credentials.Certificate(cred_dict)
        # Initialize with project ID to ensure correct database connection
        firebase_admin.initialize_app(cred, {
            'projectId': st.secrets["firebase"]["project_id"],
        })

def get_db():
    init_firebase()
    return firestore.client()

def get_auth():
    init_firebase()
    return auth
