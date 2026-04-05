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

    # Store name in Firestore
    db = get_db()
    db.collection("users").document(uid).set({"name": name, "email": email})

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

    # Fetch name from Firestore
    db = get_db()
    doc = db.collection("users").document(uid).get()
    name = doc.to_dict().get("name", email) if doc.exists else email

    return {"uid": uid, "name": name, "email": email, "id_token": id_token}
