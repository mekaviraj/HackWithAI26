# Personalized Entrance Exam Coach (MVP)

## Overview
A hackathon-ready MVP that analyzes student mock test data, detects weak topics, and generates a personalized 7-day revision plan with recommended study materials using LLM integration.

---

## Features
- Mock test error analysis (accuracy, time, failure rates)
- Weak topic detection and ranking
- Personalized 7-day revision plan (rule-based + LLM formatting)
- Study material recommendation system
- Generative AI explanations and micro notes
- Simple Streamlit dashboard UI

---

## Project Structure
```
/project_root
	 app.py
	 database.py
	 analytics.py
	 weakness_engine.py
	 planner.py
	 llm_service.py
	 recommender.py
	 sample_data/
	 requirements.txt
```

---

## Setup & Run Instructions

1. **Clone/download this repo**
2. **Install dependencies**
	```
	pip install -r requirements.txt
	```
3. **Initialize the database**
	```
	python database.py
	```
4. **(Optional) Load sample study materials into DB**
	- Use a script or insert manually from `sample_data/study_material_math.json` and `sample_data/study_material_physics.json`.
5. **Run the Streamlit app**
	```
	streamlit run app.py
	```
6. **Set your LLM API key**
	- Set environment variable `LLM_API_KEY` (e.g., for OpenAI).

---

## LLM Integration
- Uses OpenAI-compatible API (see `llm_service.py`)
- Replace `LLM_API_KEY` and `LLM_API_URL` as needed

---

## Sample Data
- `sample_data/mock_data_math.json` (math-weak student)
- `sample_data/mock_data_physics.json` (physics-weak student)
- `sample_data/study_material_math.json` (math resources)
- `sample_data/study_material_physics.json` (physics resources)

---

## Notes
- This is a minimal MVP for hackathon/demo use.
- Extend with more features and robustness as needed.
# HackWithAI26