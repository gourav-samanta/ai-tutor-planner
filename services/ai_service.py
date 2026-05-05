import json
import streamlit as st
import requests
import time

# Rate limiting
_last_call_time = 0
_min_call_interval = 1  # Faster for local Ollama

def check_ollama_available():
    """Check if Ollama is running locally"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def call_ollama(prompt: str, model: str = "deepseek-r1:7b") -> str:
    """Call local Ollama API"""
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 2000
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "")
        else:
            raise Exception(f"Ollama error: {response.status_code}")
    except Exception as e:
        raise Exception(f"Ollama call failed: {str(e)}")

def call_huggingface(prompt: str, model: str = "HuggingFaceH4/zephyr-7b-beta") -> str:
    """Call Hugging Face Inference API as fallback"""
    if "huggingface" not in st.secrets or "api_key" not in st.secrets["huggingface"]:
        raise Exception("No Hugging Face API key configured for online fallback")
    
    api_key = st.secrets["huggingface"]["api_key"]
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Format prompt for chat models
    formatted_prompt = f"<|system|>\nYou are a helpful AI assistant.</s>\n<|user|>\n{prompt}</s>\n<|assistant|>\n"
    
    payload = {
        "inputs": formatted_prompt,
        "parameters": {
            "max_new_tokens": 2000,
            "temperature": 0.7,
            "top_p": 0.95,
            "return_full_text": False,
            "do_sample": True
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "")
        return str(result)
    elif response.status_code == 503:
        raise Exception("Model is loading on Hugging Face, please wait 20 seconds and try again")
    else:
        raise Exception(f"Hugging Face API error {response.status_code}: {response.text}")

def call_ai(prompt: str, max_retries: int = 3) -> str:
    """Smart AI call - uses Ollama locally, Hugging Face online"""
    global _last_call_time
    
    # Check if Ollama is available (local)
    use_ollama = check_ollama_available()
    
    for attempt in range(max_retries):
        # Rate limiting
        current_time = time.time()
        time_since_last_call = current_time - _last_call_time
        if time_since_last_call < _min_call_interval:
            time.sleep(_min_call_interval - time_since_last_call)
        
        try:
            if use_ollama:
                result = call_ollama(prompt)
            else:
                result = call_huggingface(prompt)
            
            _last_call_time = time.time()
            return result
            
        except Exception as e:
            _last_call_time = time.time()
            error_msg = str(e)
            
            # If Ollama fails, try Hugging Face as fallback
            if use_ollama and "Ollama" in error_msg and attempt < max_retries - 1:
                use_ollama = False
                continue
            
            # If model is loading, wait and retry
            if "loading" in error_msg.lower() and attempt < max_retries - 1:
                time.sleep(20)
                continue
            
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            
            raise e
    
    raise Exception("Max retries exceeded")

def call_ai_json(prompt: str, max_attempts: int = 3):
    """Call AI and parse JSON response"""
    for attempt in range(max_attempts):
        try:
            raw = call_ai(prompt)
            # Clean markdown code blocks
            cleaned = raw.strip()
            
            # Remove markdown code blocks
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            # Find JSON in response
            start_idx = min(
                cleaned.find('[') if '[' in cleaned else len(cleaned),
                cleaned.find('{') if '{' in cleaned else len(cleaned)
            )
            
            if start_idx < len(cleaned):
                if cleaned[start_idx] == '[':
                    end_idx = cleaned.rfind(']')
                else:
                    end_idx = cleaned.rfind('}')
                
                if end_idx > start_idx:
                    json_str = cleaned[start_idx:end_idx+1]
                    return json.loads(json_str)
            
            return json.loads(cleaned)
            
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(2)
                continue
            raise e
    
    raise Exception("Failed to parse JSON after multiple attempts")

def generate_roadmap(topic, purpose, duration, daily_hours, level) -> list:
    prompt = f"""You are an expert learning planner. Generate a structured learning roadmap in JSON format.
Topic: {topic}
Purpose: {purpose}
Duration: {duration}
Daily time: {daily_hours} hours
Level: {level}

Return ONLY a JSON array (no markdown, no explanation):
[
  {{
    "week": 1,
    "title": "Week title",
    "topics": ["topic1", "topic2"],
    "keyConcepts": ["concept1", "concept2"],
    "expectedOutcome": "What learner will achieve"
  }}
]

Generate a roadmap with appropriate number of weeks based on duration."""
    return call_ai_json(prompt)

def generate_daily_tasks(topic, level, daily_hours, date) -> list:
    prompt = f"""You are a learning task generator. Generate daily tasks in JSON format.
Topic: {topic}
Level: {level}
Daily time available: {daily_hours} hours
Date: {date}

Return ONLY a JSON array (no markdown):
[
  {{
    "id": "unique_id_string",
    "title": "Task title",
    "description": "What to do",
    "estimatedTime": "30 mins",
    "difficulty": "easy",
    "type": "reading"
  }}
]

Generate 8-12 tasks based on daily hours. difficulty: easy|medium|hard. type: reading|video|practice|revision."""
    tasks = call_ai_json(prompt)
    return [{"completed": False, "carriedOver": False, **t} for t in tasks]

def generate_test(topic, level, test_type) -> list:
    count = "15-20" if test_type == "weekly" else "5-8"
    prompt = f"""Generate a {test_type} test for a learner studying {topic} at {level} level.
Return ONLY a JSON array (no markdown):
[
  {{
    "question": "Question text",
    "type": "mcq",
    "options": ["A", "B", "C", "D"],
    "answer": "correct answer"
  }}
]

Generate {count} questions. For short answer, options = []. type: mcq|short."""
    return call_ai_json(prompt)

def generate_ai_summary(records: list) -> str:
    if not records:
        return ""
    
    # Cache key based on records
    cache_key = f"summary_{len(records)}_{sum(r.get('daily_score', 0) for r in records)}"
    
    # Check cache
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    avg = sum(r.get("daily_score", 0) for r in records) / len(records)
    completions = ", ".join(str(r.get("task_completion", 0)) + "%" for r in records)
    prompt = f"""A student has an average daily score of {avg:.0f}% over {len(records)} days.
Task completion rates: {completions}.
Give a short 3-sentence performance summary: strengths, weaknesses, one improvement tip. Be direct."""
    
    try:
        result = call_ai(prompt)
        st.session_state[cache_key] = result
        return result
    except Exception as e:
        if avg >= 70:
            return f"Good progress! You're maintaining an average score of {avg:.0f}%. Keep up the consistent effort."
        elif avg >= 50:
            return f"You're making progress with an average of {avg:.0f}%. Try to increase your daily task completion rate for better results."
        else:
            return f"Your average score is {avg:.0f}%. Focus on completing more daily tasks and reviewing the material regularly."

def generate_task_learning_content(task_title: str, task_description: str, topic: str, level: str) -> str:
    """Generate learning content for a specific task"""
    prompt = f"""You are a helpful tutor. A student is learning {topic} at {level} level.
They have a task: "{task_title}"
Description: {task_description}

Provide a concise, helpful explanation (200-300 words) covering:
1. Key concepts related to this task
2. Important points to understand
3. A simple example or analogy
4. Quick tips for completing this task

Be clear, practical, and encouraging."""
    
    try:
        return call_ai(prompt)
    except Exception as e:
        return f"⚠️ Unable to generate learning content. Error: {str(e)}\n\nPlease try again or search online for: {task_title}"

def get_api_key_status():
    """Get status for debugging"""
    ollama_available = check_ollama_available()
    
    if ollama_available:
        return {
            "provider": "Ollama (Local)",
            "model": "deepseek-r1:7b",
            "rate_limit": "Unlimited (local)",
            "status": "active",
            "fallback": "Hugging Face (if Ollama fails)"
        }
    else:
        return {
            "provider": "Hugging Face (Online)",
            "model": "Zephyr-7B-Beta",
            "rate_limit": "1000 requests/day",
            "status": "active",
            "note": "Install Ollama locally for unlimited requests"
        }
