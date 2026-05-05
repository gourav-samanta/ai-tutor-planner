# Setup Ollama for Local AI (Unlimited & Free!)

## What This Does:
- **Local (your computer)**: Uses Ollama with DeepSeek-R1 7B - **UNLIMITED & FREE**
- **Online (Streamlit Cloud)**: Automatically falls back to Hugging Face API
- **Best of both worlds**: Free unlimited local use, online still works

## Step 1: Install Ollama

### Windows:
1. Download: https://ollama.com/download/windows
2. Run the installer
3. Ollama will start automatically

### Mac:
```bash
brew install ollama
```

### Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Step 2: Download DeepSeek Model

Open terminal/command prompt:
```bash
ollama pull deepseek-r1:7b
```

This downloads the 7B model (~4.7GB). Wait for it to complete.

## Step 3: Verify Ollama is Running

```bash
ollama list
```

You should see `deepseek-r1:7b` in the list.

Test it:
```bash
ollama run deepseek-r1:7b "Hello, how are you?"
```

## Step 4: Get Hugging Face Token (for online fallback)

1. Go to https://huggingface.co/settings/tokens
2. Create new token
3. Check only: **"Make calls to Inference Providers"**
4. Copy the token (starts with `hf_...`)

## Step 5: Update Secrets

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

## Step 6: Switch to Hybrid Service

```bash
cd ai-tutor-planner-python

# Backup current service
cp services/ai_service.py services/ai_service_gemini_backup.py

# Switch to hybrid (Ollama + Hugging Face)
cp services/ai_service_hybrid.py services/ai_service.py

# Commit and push
git add services/ai_service.py
git commit -m "Switch to Ollama (local) + Hugging Face (online) hybrid"
git push
```

## Step 7: Test Locally

```bash
streamlit run app.py
```

Check the API status in the app - it should show "Ollama (Local)".

## How It Works:

### When Running Locally:
1. App checks if Ollama is available at `http://localhost:11434`
2. If yes → Uses Ollama (unlimited, free, fast)
3. If no → Falls back to Hugging Face

### When Deployed on Streamlit Cloud:
1. Ollama not available (no localhost)
2. Automatically uses Hugging Face API
3. 1000 requests/day limit

## Benefits:

✅ **Local Development**: Unlimited free AI calls
✅ **Online Production**: Still works with Hugging Face
✅ **No Code Changes**: Automatic detection
✅ **Fast**: Local inference is faster than API calls
✅ **Privacy**: Local data stays local

## Troubleshooting:

### Ollama not detected:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it:
ollama serve
```

### Model not found:
```bash
# Pull the model again
ollama pull deepseek-r1:7b
```

### Want to use a different model:
Edit `ai_service_hybrid.py` line 18:
```python
def call_ollama(prompt: str, model: str = "llama3.2:3b") -> str:
```

Available models:
- `deepseek-r1:7b` (recommended, 4.7GB)
- `llama3.2:3b` (smaller, faster, 2GB)
- `mistral:7b` (good balance, 4.1GB)
- `qwen2.5:7b` (multilingual, 4.7GB)

## System Requirements:

- **RAM**: 8GB minimum (16GB recommended for 7B models)
- **Storage**: 5-10GB for model
- **GPU**: Optional (CPU works fine, just slower)

## Performance:

- **With GPU**: ~50 tokens/second
- **CPU only**: ~5-10 tokens/second
- Still faster than waiting for API rate limits!
