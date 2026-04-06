import json
import streamlit as st
import google.generativeai as genai

def get_client():
    genai.configure(api_key=st.secrets["gemini"]["api_key"])
    return genai.GenerativeModel('gemini-pro')

def call_ai(prompt: str) -> str:
    model = get_client()
    response = model.generate_content(prompt)
    return response.text

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
    raw = call_ai(prompt)
    # Clean markdown code blocks if present
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return json.loads(raw.strip())

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
Generate 4-6 tasks. difficulty: easy|medium|hard. type: reading|video|practice|revision."""
    raw = call_ai(prompt)
    # Clean markdown code blocks if present
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    tasks = json.loads(raw.strip())
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
    raw = call_ai(prompt)
    # Clean markdown code blocks if present
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return json.loads(raw.strip())

def generate_ai_summary(records: list) -> str:
    if not records:
        return ""
    avg = sum(r.get("daily_score", 0) for r in records) / len(records)
    completions = ", ".join(str(r.get("task_completion", 0)) + "%" for r in records)
    prompt = f"""A student has an average daily score of {avg:.0f}% over {len(records)} days.
Task completion rates: {completions}.
Give a short 3-sentence performance summary: strengths, weaknesses, one improvement tip. Be direct."""
    return call_ai(prompt)
