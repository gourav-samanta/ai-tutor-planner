import requests
import streamlit as st
from services.firebase import get_db, get_auth

FIREBASE_API_KEY = None

def _get_api_key():
    return st.secrets["firebase_web"]["api_key"]

def signup(name: str, email: str, password: str):
    """Create user via Firebase REST API, store profile in Firestore."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={_get_api_key()}"
    resp = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True})
    data = resp.json()
    if "error" in data:
        raise Exception(data["error"]["message"])

    uid = data["localId"]
    id_token = data["idToken"]

    # Try to store name in Firestore, but don't fail if database isn't ready
    try:
        db = get_db()
        db.collection("users").document(uid).set({"name": name, "email": email})
    except Exception as e:
        # Log the error but continue - user is created in Auth
        print(f"Warning: Could not store user profile in Firestore: {e}")
        # Store name in session for now
        pass

    return {"uid": uid, "name": name, "email": email, "id_token": id_token}

def login(email: str, password: str):
    """Sign in via Firebase REST API."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={_get_api_key()}"
    resp = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True})
    data = resp.json()
    if "error" in data:
        raise Exception(data["error"]["message"])

    uid = data["localId"]
    id_token = data["idToken"]

    # Try to fetch name from Firestore, use email as fallback
    name = email
    try:
        db = get_db()
        doc = db.collection("users").document(uid).get()
        if doc.exists:
            name = doc.to_dict().get("name", email)
    except Exception as e:
        # If Firestore isn't ready, just use email as name
        print(f"Warning: Could not fetch user profile from Firestore: {e}")
        pass

    return {"uid": uid, "name": name, "email": email, "id_token": id_token}
