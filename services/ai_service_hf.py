import json
import streamlit as st
import requests
import time

# Rate limiting
_last_call_time = 0
_min_call_interval = 2  # Hugging Face has better limits

def get_hf_api_key():
    """Get Hugging Face API key from secrets"""
    if "huggingface" in st.secrets and "api_key" in st.secrets["huggingface"]:
        return st.secrets["huggingface"]["api_key"]
    raise ValueError("No Hugging Face API key found. Add [huggingface] api_key to secrets.")

def call_huggingface_api(prompt: str, model: str = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B", max_retries: int = 3) -> str:
    """Call Hugging Face Inference API"""
    global _last_call_time
    
    api_key = get_hf_api_key()
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    for attempt in range(max_retries):
        # Rate limiting
        current_time = time.time()
        time_since_last_call = current_time - _last_call_time
        if time_since_last_call < _min_call_interval:
            time.sleep(_min_call_interval - time_since_last_call)
        
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 2000,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "return_full_text": False
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            _last_call_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
                return str(result)
            elif response.status_code == 503:
                # Model is loading, wait and retry
                if attempt < max_retries - 1:
                    time.sleep(20)  # Wait for model to load
                    continue
            else:
                raise Exception(f"API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            raise e
    
    raise Exception("Max retries exceeded")

def call_ai(prompt: str) -> str:
    """Main AI call function - uses Hugging Face"""
    return call_huggingface_api(prompt)

def call_ai_json(prompt: str, max_attempts: int = 3):
    """Call AI and parse JSON response"""
    for attempt in range(max_attempts):
        try:
            raw = call_ai(prompt)
            # Clean markdown code blocks
            cleaned = raw.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            # Try to find JSON in the response
            cleaned = cleaned.strip()
            
            # Find first [ or { and last ] or }
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
            
            # If no brackets found, try parsing the whole thing
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
        # Cache the result
        st.session_state[cache_key] = result
        return result
    except Exception as e:
        # Return a fallback message if AI fails
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
        return f"⚠️ Unable to generate learning content at the moment. Error: {str(e)}\n\nPlease try again later or search online for: {task_title}"

def get_api_key_status():
    """Get status for debugging"""
    return {
        "provider": "Hugging Face",
        "model": "DeepSeek-R1-Distill-Llama-8B",
        "rate_limit": "1000 requests/day",
        "status": "active"
    }
