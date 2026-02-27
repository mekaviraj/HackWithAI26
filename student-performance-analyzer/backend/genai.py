import json
import os
import logging
import re
from typing import Any, Dict, Optional, List

import requests

# API key and model hardcoded
API_KEY = "AIzaSyAe1T9WBkTI-D5NMwZyfgSPTAbkaki54Vw"
# Use "auto" to select the first available generateContent model.
GEMINI_MODEL = "auto"
API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
logger = logging.getLogger(__name__)
_CACHED_MODEL: Optional[str] = None


def generate_study_guidance(analysis: Dict[str, Any], rag_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Generate study guidance using Gemini API with RAG context"""
    api_key = API_KEY
    
    if not api_key or api_key.strip() == "":
        logger.error("GenAI: API key is empty or not set")
        print("[ERROR] GenAI: No API key found.")
        return None
    
    # Debug: confirm key is loaded
    key_preview = api_key[:10] + "..." if len(api_key) > 10 else api_key
    logger.info(f"GenAI: API key loaded ({key_preview})")
    logger.info(f"GenAI: Model config = {GEMINI_MODEL}")
    print(f"[DEBUG] GenAI: API key loaded ({key_preview})")
    print(f"[DEBUG] GenAI: Model config = {GEMINI_MODEL}")

    summary = analysis.get("summary", {})
    prompt = _build_prompt(analysis, summary, rag_context)
    logger.debug(f"GenAI: Prompt built (length: {len(prompt)})")

    try:
        response_text = _call_gemini(api_key, prompt)
        logger.debug(f"GenAI: Raw response (first 200 chars): {response_text[:200]}")
        
        payload = _parse_json(response_text)
        if not payload:
            logger.error("GenAI: Failed to parse JSON from response")
            print("[ERROR] GenAI: Failed to parse JSON response")
            print(f"[DEBUG] Response was: {response_text[:300]}")

            repaired_text = _repair_json(api_key, response_text)
            if repaired_text:
                payload = _parse_json(repaired_text)
                if not payload:
                    logger.error("GenAI: Failed to parse repaired JSON response")
                    return None
            else:
                return None
        
        if not _validate_payload(payload):
            logger.error("GenAI: Payload validation failed")
            print("[ERROR] GenAI: Payload validation failed")
            print(f"[DEBUG] Payload was: {json.dumps(payload, indent=2)[:500]}")
            return None
        
        logger.info("GenAI: ✓ Successfully generated guidance")
        print("[SUCCESS] GenAI: Guidance generated successfully")
        return payload
    
    except requests.RequestException as exc:
        logger.error(f"GenAI: API request failed: {exc}", exc_info=True)
        print(f"[ERROR] GenAI API request failed: {exc}")
        return None
    except Exception as exc:
        logger.error(f"GenAI: Unexpected error: {exc}", exc_info=True)
        print(f"[ERROR] GenAI: Unexpected error: {exc}")
        return None


def _build_prompt(analysis: Dict[str, Any], summary: Dict[str, Any], rag_context: Dict[str, Any]) -> str:
    """Build a detailed prompt for GenAI with analysis data and RAG context"""
    subtopics = analysis.get("subtopic_ranking", [])
    accuracy_by_difficulty = analysis.get("accuracy_by_difficulty", [])
    time_comparison = analysis.get("time_comparison", {})
    strength_level = summary.get("strength_level", "Developing")

    # Format subtopics by accuracy
    weak_subtopics = subtopics[:3] if len(subtopics) > 3 else subtopics
    
    # Format RAG context nicely
    rag_resources_text = "AVAILABLE RESOURCES:\n"
    for subtopic, resources in rag_context.items():
        if resources:
            rag_resources_text += f"\n{subtopic}:\n"
            for i, res in enumerate(resources, 1):
                rag_resources_text += f"  {i}. {res.get('name', '')} [{res.get('type', '')}]\n"
                rag_resources_text += f"     URL: {res.get('url', '')}\n"
        else:
            rag_resources_text += f"\n{subtopic}: [No resources available]\n"

    prompt = (
        "You are an expert education coach. Generate a personalized 7-day study plan based on the student's performance.\n\n"
        
        "STUDENT PERFORMANCE DATA:\n"
        f"- Strength Level: {strength_level}\n"
        f"- Total Attempts: {summary.get('total_attempts', 0)}\n"
        f"- Overall Accuracy: {summary.get('overall_accuracy', 0):.1f}%\n"
        f"- Weakest Subtopics: {', '.join([s['subtopic'] for s in weak_subtopics])}\n\n"
        
        "ACCURACY BY DIFFICULTY:\n"
        + "\n".join([f"- Difficulty {d['difficulty']}: {d['accuracy']:.1f}% ({d['attempts']} attempts)" 
                     for d in accuracy_by_difficulty]) + "\n\n"
        
        "TIME ANALYSIS:\n"
        f"- Avg time for correct answers: {time_comparison.get('avg_time_correct', 0):.1f}s\n"
        f"- Avg time for incorrect answers: {time_comparison.get('avg_time_incorrect', 0):.1f}s\n\n"
        
        + rag_resources_text + "\n\n"
        
        "REQUIREMENTS:\n"
        "1. Create EXACTLY 7 days of study plan (no more, no less)\n"
        "2. Focus heavily on the weakest subtopics (lowest accuracy)\n"
        "3. Each day must have: day, date (YYYY-MM-DD), focus (list of subtopics), study_time (string), activities (list), goals (list)\n"
        "4. Recommendations must ONLY include resources from the available resources above\n"
        "5. Study tips should be specific and actionable\n"
        "6. Keep activities and goals to at most 2 items each\n"
        "7. Keep study tips to at most 2 items each\n"
        "8. Return ONLY valid JSON (no markdown, no code fences, no extra text) matching this schema:\n"
        "{\n"
        '  "plan": [{"day": 1, "date": "YYYY-MM-DD", "focus": ["subtopic"], "study_time": "2-3 hours", "activities": ["..."], "goals": ["..."]}],\n'
        '  "recommendations": {"subtopic": [{"name": "...", "url": "...", "type": "..."}]},\n'
        '  "study_tips": {"subtopic": ["tip1", "tip2", "tip3"]}\n'
        "}\n\n"
        
        "START YOUR RESPONSE WITH { (begin JSON immediately)"
    )

    return prompt


def _call_gemini(api_key: str, prompt: str) -> str:
    """Call Gemini API and return the text response"""
    model = _select_model(api_key)
    url = f"{API_BASE_URL}/{model}:generateContent?key={api_key}"
    
    logger.info(f"GenAI: Calling {model} API")
    logger.debug(f"GenAI: URL = {url[:100]}...")
    print(f"[DEBUG] GenAI: Calling {model} API")
    print(f"[DEBUG] GenAI: URL = {url[:100]}...")

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "topP": 0.9,
            "maxOutputTokens": 4096,
            "responseMimeType": "application/json",
        },
    }

    logger.debug(f"GenAI: Request payload built (size: {len(json.dumps(payload))} bytes)")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        logger.info(f"GenAI: API response status {response.status_code}")
        print(f"[DEBUG] GenAI: API response status {response.status_code}")
        
        if response.status_code != 200:
            error_text = response.text[:500]
            logger.error(f"GenAI API error ({response.status_code}): {error_text}")
            print(f"[ERROR] GenAI API error ({response.status_code}): {error_text}")
            response.raise_for_status()
        
        data = response.json()
        logger.debug(f"GenAI: Response JSON keys: {list(data.keys())}")

        candidates = data.get("candidates", [])
        if not candidates:
            raise requests.RequestException("No candidates returned from Gemini API")

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            raise requests.RequestException("No content parts returned from Gemini API")

        text = parts[0].get("text", "")
        if not text:
            raise requests.RequestException("Empty text in Gemini response")
        
        logger.debug(f"GenAI: Response text length: {len(text)}")
        return text
    
    except requests.Timeout as e:
        logger.error(f"GenAI: Request timeout after 30s: {e}")
        raise requests.RequestException(f"Gemini API timeout: {e}")
    except requests.ConnectionError as e:
        logger.error(f"GenAI: Connection error: {e}")
        raise requests.RequestException(f"Gemini API connection error: {e}")
    except Exception as e:
        logger.error(f"GenAI: Unexpected error in API call: {e}", exc_info=True)
        raise


def _select_model(api_key: str) -> str:
    """Select a model that supports generateContent, with caching."""
    global _CACHED_MODEL
    if GEMINI_MODEL and GEMINI_MODEL != "auto":
        return GEMINI_MODEL
    if _CACHED_MODEL:
        return _CACHED_MODEL

    models = _list_models(api_key)
    if not models:
        raise requests.RequestException("No models returned from Gemini API")

    preferred = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-1.5-pro-latest",
        "gemini-pro",
    ]

    for name in preferred:
        if name in models:
            _CACHED_MODEL = name
            return name

    _CACHED_MODEL = models[0]
    return _CACHED_MODEL


def _list_models(api_key: str) -> List[str]:
    """Return model names that support generateContent."""
    url = f"{API_BASE_URL}?key={api_key}"
    response = requests.get(url, timeout=15)
    if response.status_code != 200:
        raise requests.RequestException(
            f"ListModels failed: {response.status_code} {response.text[:200]}"
        )

    data = response.json()
    items = data.get("models", [])
    supported = []
    for item in items:
        name = item.get("name", "")
        methods = item.get("supportedGenerationMethods", [])
        if "generateContent" in methods and name:
            supported.append(name)

    normalized = [name.split("/")[-1] for name in supported]
    if not normalized:
        logger.error("GenAI: No models support generateContent")
    else:
        logger.info(f"GenAI: Available models = {normalized}")
    return normalized


def _repair_json(api_key: str, raw_text: str) -> Optional[str]:
    """Ask the model to repair invalid JSON and return corrected JSON text."""
    if not raw_text:
        return None

    snippet = raw_text[:8000]
    repair_prompt = (
        "Fix the JSON below so it is valid and matches the required schema. "
        "Return ONLY valid JSON, no markdown or code fences.\n\n"
        f"JSON TO FIX:\n{snippet}"
    )

    try:
        return _call_gemini(api_key, repair_prompt)
    except requests.RequestException as exc:
        logger.error(f"GenAI: JSON repair request failed: {exc}")
        return None


def _parse_json(text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse JSON from response text"""
    if not text or not isinstance(text, str):
        logger.error(f"_parse_json: Invalid input type: {type(text)}")
        return None

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\s*", "", cleaned)
        if cleaned.endswith("```"):
            cleaned = cleaned[: -3].rstrip()

    # Find JSON object boundaries
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    
    if start == -1 or end == -1 or start >= end:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            logger.error("_parse_json: No JSON boundaries found in text")
            return None
        json_str = match.group(0)
    else:
        json_str = cleaned[start:end + 1]
    logger.debug(f"_parse_json: Extracted JSON string (length: {len(json_str)})")
    
    try:
        parsed = json.loads(json_str)
        logger.debug(f"_parse_json: Successfully parsed JSON with keys: {list(parsed.keys())}")
        return parsed
    except json.JSONDecodeError as e:
        logger.error(f"_parse_json: JSON decode error at line {e.lineno}, col {e.colno}: {e.msg}")
        logger.error(f"_parse_json: Problem area: {json_str[max(0, e.pos-50):e.pos+50]}")
        return None


def _validate_payload(payload: Dict[str, Any]) -> bool:
    """Validate GenAI payload structure and content"""
    if not isinstance(payload, dict):
        logger.error(f"_validate_payload: Payload is not a dict: {type(payload)}")
        return False
    
    # Check top-level keys
    plan = payload.get("plan")
    recommendations = payload.get("recommendations")
    study_tips = payload.get("study_tips")

    if plan is None:
        logger.error("_validate_payload: Missing 'plan' key")
        return False
    if recommendations is None:
        logger.error("_validate_payload: Missing 'recommendations' key")
        return False
    if study_tips is None:
        logger.error("_validate_payload: Missing 'study_tips' key")
        return False

    # Validate plan
    if not isinstance(plan, list):
        logger.error(f"_validate_payload: 'plan' is not a list: {type(plan)}")
        return False
    if len(plan) != 7:
        logger.error(f"_validate_payload: 'plan' has {len(plan)} days, expected 7")
        return False

    for day_idx, day in enumerate(plan):
        if not isinstance(day, dict):
            logger.error(f"_validate_payload: plan[{day_idx}] is not a dict")
            return False
        
        required_keys = ["day", "date", "focus", "study_time", "activities", "goals"]
        for key in required_keys:
            if key not in day:
                logger.error(f"_validate_payload: plan[{day_idx}] missing key '{key}'")
                return False
        
        if not isinstance(day["focus"], list):
            logger.error(f"_validate_payload: plan[{day_idx}]['focus'] is not a list")
            return False
        if not isinstance(day["activities"], list):
            logger.error(f"_validate_payload: plan[{day_idx}]['activities'] is not a list")
            return False
        if not isinstance(day["goals"], list):
            logger.error(f"_validate_payload: plan[{day_idx}]['goals'] is not a list")
            return False

    # Validate recommendations
    if not isinstance(recommendations, dict):
        logger.error(f"_validate_payload: 'recommendations' is not a dict: {type(recommendations)}")
        return False

    for subtopic, resources in recommendations.items():
        if not isinstance(subtopic, str):
            logger.error(f"_validate_payload: recommendations key is not a str")
            return False
        if not isinstance(resources, list):
            logger.error(f"_validate_payload: recommendations['{subtopic}'] is not a list")
            return False
        for res_idx, resource in enumerate(resources):
            if not isinstance(resource, dict):
                logger.error(f"_validate_payload: recommendations['{subtopic}'][{res_idx}] is not a dict")
                return False
            for key in ["name", "url", "type"]:
                if key not in resource:
                    logger.error(f"_validate_payload: recommendations['{subtopic}'][{res_idx}] missing key '{key}'")
                    return False

    # Validate study_tips
    if not isinstance(study_tips, dict):
        logger.error(f"_validate_payload: 'study_tips' is not a dict: {type(study_tips)}")
        return False

    for subtopic, tips in study_tips.items():
        if not isinstance(subtopic, str):
            logger.error(f"_validate_payload: study_tips key is not a str")
            return False
        if not isinstance(tips, list):
            logger.error(f"_validate_payload: study_tips['{subtopic}'] is not a list")
            return False
        if not all(isinstance(tip, str) for tip in tips):
            logger.error(f"_validate_payload: study_tips['{subtopic}'] contains non-string elements")
            return False

    logger.info("_validate_payload: ✓ Payload validation successful")
    return True
