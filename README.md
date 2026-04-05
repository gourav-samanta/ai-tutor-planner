# AI Tutor Planner (Python + Streamlit)

## Stack
- Frontend: Streamlit
- Database: Firebase Firestore
- Auth: Firebase Authentication (REST API)
- AI: OpenAI GPT-3.5

## Local Setup

```bash
cd ai-tutor-planner-python
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Fill in secrets.toml (see below)
streamlit run app.py
```

## secrets.toml Setup

### Firebase (from Service Account JSON)
Go to Firebase Console → Project Settings → Service Accounts → Generate new private key

### OpenAI
Get key from platform.openai.com

### Firebase Web API Key
Firebase Console → Project Settings → General → Web API Key

## Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to share.streamlit.io → New app → select repo
3. Add secrets in the Streamlit Cloud dashboard under App Settings → Secrets
   (paste the contents of your secrets.toml)

## Firestore Collections
- users · plans · tasks · tests · progress
