"""
llm_service.py
Handles LLM API calls for explanations, plan formatting, and micro notes.
"""
import os
import requests

LLM_API_URL = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
LLM_API_KEY = os.getenv("LLM_API_KEY", "sk-...YOUR_KEY...")

HEADERS = {
    "Authorization": f"Bearer {LLM_API_KEY}",
    "Content-Type": "application/json"
}

def call_llm(messages, model="gpt-3.5-turbo", max_tokens=512):
    try:
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        resp = requests.post(LLM_API_URL, headers=HEADERS, json=payload, timeout=20)
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"LLM API Error: {e}"

def generate_weakness_explanation(topic_json):
    messages = [
        {"role": "system", "content": "You are an expert exam coach."},
        {"role": "user", "content": f"Analyze this topic performance and explain why the student is weak. Reply in JSON with a short explanation.\n{topic_json}"}
    ]
    return call_llm(messages)

def format_7_day_plan(plan_json):
    messages = [
        {"role": "system", "content": "You are an expert exam coach."},
        {"role": "user", "content": f"Convert this 7-day revision plan into a readable JSON with daily topic, study type, estimated time, and a short focus instruction. Limit to 3 hours/day.\n{plan_json}"}
    ]
    return call_llm(messages)

def generate_micro_notes(topic):
    messages = [
        {"role": "system", "content": "You are an expert exam coach."},
        {"role": "user", "content": f"For the topic '{topic}', generate: 5 key concepts, 5 formulas, 3 common mistakes. Reply in JSON."}
    ]
    return call_llm(messages)
