import json
import streamlit as st
import google.generativeai as genai
import time

# Rate limiting
_last_call_time = 0
_min_call_interval = 15  # seconds between calls (increased to avoid rate limits)

# API key rotation
_current_key_index = 0
_failed_keys = set()  # Track keys that have hit quota
_key_last_used = {}  # Track when each key was last used

def _get_api_keys():
    """Return configured Gemini API keys in normalized list form."""
    if "api_keys" in st.secrets["gemini"]:
        return st.secrets["gemini"]["api_keys"]
    if "api_key" in st.secrets["gemini"]:
        return [st.secrets["gemini"]["api_key"]]
    raise ValueError("No API keys found in secrets. Please add 'api_keys' array or 'api_key' to [gemini] section.")

def get_next_api_key():
    """Get next available API key using rotation strategy"""
    global _current_key_index
    api_keys = _get_api_keys()
    
    # If all keys have failed, reset the failed set (they might work again after time)
    if len(_failed_keys) >= len(api_keys):
        _failed_keys.clear()
    
    # Try to find a key that hasn't failed
    attempts = 0
    while attempts < len(api_keys):
        key = api_keys[_current_key_index]
        _current_key_index = (_current_key_index + 1) % len(api_keys)
        
        if key not in _failed_keys:
            return key
        
        attempts += 1
    
    # If all keys are marked as failed, return the next one anyway (reset scenario)
    return api_keys[_current_key_index]

def mark_key_as_failed(api_key):
    """Mark an API key as failed for the current session"""
    _failed_keys.add(api_key)

def get_client():
    api_key = get_next_api_key()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash'), api_key

def call_ai(prompt: str, max_retries: int | None = None) -> str:
    global _last_call_time, _key_last_used
    api_keys = _get_api_keys()
    if max_retries is None:
        max_retries = len(api_keys)

    last_error = None
    
    for attempt in range(max_retries):
        # Rate limiting: wait if needed
        current_time = time.time()
        time_since_last_call = current_time - _last_call_time
        if time_since_last_call < _min_call_interval:
            wait_time = _min_call_interval - time_since_last_call
            time.sleep(wait_time)
        
        model, api_key = get_client()
        
        # Check if this specific key was used recently
        if api_key in _key_last_used:
            time_since_key_used = time.time() - _key_last_used[api_key]
            if time_since_key_used < 15:  # Wait at least 15 seconds per key
                time.sleep(15 - time_since_key_used)
        
        try:
            response = model.generate_content(prompt)
            _last_call_time = time.time()
            _key_last_used[api_key] = time.time()
            return response.text
        except Exception as e:
            _last_call_time = time.time()
            _key_last_used[api_key] = time.time()
            error_msg = str(e)
            last_error = e

            # Any failed attempt should rotate to the next key.
            mark_key_as_failed(api_key)

            # Extract retry delay if available for quota/rate responses.
            if "retry in" in error_msg.lower():
                try:
                    import re
                    match = re.search(r'retry in (\d+\.?\d*)', error_msg.lower())
                    if match and attempt < max_retries - 1:
                        retry_seconds = float(match.group(1))
                        time.sleep(min(retry_seconds, 40))  # Cap at 40 seconds
                except:
                    pass

            if attempt < max_retries - 1:
                time.sleep(3)  # Brief delay before trying the next key
                continue

            raise e
    
    # If all retries failed, raise the last error
    raise last_error

def call_ai_json(prompt: str, max_attempts: int | None = None):
    """Call Gemini until we get valid JSON or all keys have been exhausted."""
    if max_attempts is None:
        max_attempts = len(_get_api_keys())

    last_error = None

    for attempt in range(max_attempts):
        try:
            raw = call_ai(prompt, max_retries=1)
            cleaned = raw.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except Exception as e:
            last_error = e

            # If the model returned unusable output, rotate away from the current key
            # and try again with the next one.
            if attempt < max_attempts - 1:
                time.sleep(2)
                continue

            raise e

    raise last_error

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
]"""
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

Be clear, practical, and encouraging. Format with markdown for readability."""
    
    try:
        return call_ai(prompt)
    except Exception as e:
        return f"⚠️ Unable to generate learning content at the moment. Error: {str(e)}\n\nPlease try again later or search online for: {task_title}"
