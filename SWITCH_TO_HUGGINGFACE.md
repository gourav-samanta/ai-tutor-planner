# Switch to Hugging Face API

## Step 1: Get Hugging Face API Key

1. Go to https://huggingface.co/settings/tokens
2. Create a new token (Read access is enough)
3. Copy the token

## Step 2: Update Secrets

### Local (.streamlit/secrets.toml):
```toml
[huggingface]
api_key = "hf_YOUR_TOKEN_HERE"
```

### Streamlit Cloud (Settings → Secrets):
```toml
[huggingface]
api_key = "hf_YOUR_TOKEN_HERE"
```

## Step 3: Switch the AI Service

Run this command to switch:

```bash
# Backup current service
cp services/ai_service.py services/ai_service_gemini_backup.py

# Switch to Hugging Face
cp services/ai_service_hf.py services/ai_service.py
```

Or manually:
1. Rename `services/ai_service.py` to `services/ai_service_gemini_backup.py`
2. Rename `services/ai_service_hf.py` to `services/ai_service.py`

## Step 4: Update requirements.txt

Add this line if not present:
```
requests
```

## Step 5: Commit and Push

```bash
git add services/ai_service.py requirements.txt .streamlit/secrets.toml
git commit -m "Switch to Hugging Face API"
git push
```

## Benefits of Hugging Face:

- **1000 requests per day** (vs 15-20 for Gemini free tier)
- Free inference API
- No leaked key issues
- DeepSeek-R1 is a powerful open-source model
- Better for production use

## Alternative Models:

You can also use these models by changing the model parameter:
- `meta-llama/Llama-3.2-3B-Instruct` (faster, lighter)
- `mistralai/Mistral-7B-Instruct-v0.3` (good balance)
- `Qwen/Qwen2.5-7B-Instruct` (multilingual)

Just update the model name in `ai_service_hf.py` line 13.
