"""
app.py
Streamlit UI for Personalized Entrance Exam Coach MVP
"""
import streamlit as st
import json
from database import init_db
from analytics import get_topic_performance
from weakness_engine import get_top_weak_topics
from planner import allocate_7_day_plan
from llm_service import generate_weakness_explanation, format_7_day_plan, generate_micro_notes
from recommender import recommend_for_weak_topics

st.set_page_config(page_title="Entrance Exam Coach", layout="centered")
st.title("🎓 Personalized Entrance Exam Coach")

# --- DB Init ---
init_db()

# --- Data Load ---
st.sidebar.header("Load Sample Data")
sample = st.sidebar.selectbox("Choose student sample:", ["Math Weak", "Physics Weak"])
if sample == "Math Weak":
    data_file = "sample_data/mock_data_math.json"
    student_id = 1
else:
    data_file = "sample_data/mock_data_physics.json"
    student_id = 2

if st.sidebar.button("Load Data"):
    # Load and insert data into DB
    import sqlite3
    from database import get_connection
    with open(data_file) as f:
        data = json.load(f)
    conn = get_connection()
    c = conn.cursor()
    # Insert student
    c.execute("INSERT OR IGNORE INTO students (student_id, name) VALUES (?, ?)", (student_id, sample))
    # Insert mock test and questions
    test_id = data[0]['test_id']
    c.execute("INSERT OR IGNORE INTO mock_tests (test_id, student_id, date) VALUES (?, ?, ?)", (test_id, student_id, "2026-02-27"))
    for q in data:
        c.execute("INSERT OR IGNORE INTO questions (question_id, test_id, subject, topic, subtopic, difficulty_level, is_correct, time_taken) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (q['question_id'], q['test_id'], q['subject'], q['topic'], q['subtopic'], q['difficulty_level'], int(q['is_correct']), q['time_taken']))
    conn.commit()
    conn.close()
    st.success("Sample data loaded!")

# --- Analysis ---
if st.button("Analyze Performance"):
    perf = get_topic_performance(student_id)
    st.subheader("Topic Accuracy")
    topics = list(perf['topic_performance'].keys())
    accuracies = [perf['topic_performance'][t]['accuracy'] for t in topics]
    st.bar_chart({"Accuracy": accuracies}, x=topics)

    st.subheader("Weakness Ranking")
    weak = get_top_weak_topics(perf['topic_performance'])
    st.table(weak['weak_topics'])

    st.subheader("AI Explanation")
    exp = generate_weakness_explanation(json.dumps(perf['topic_performance']))
    st.json(exp)

    st.subheader("7-Day Revision Plan")
    plan = allocate_7_day_plan(weak['weak_topics'])
    plan_str = format_7_day_plan(json.dumps(plan))
    st.json(plan_str)

    st.subheader("Recommended Study Materials")
    recs = recommend_for_weak_topics(weak['weak_topics'])
    st.json(recs)

    st.subheader("Micro Revision Notes (Demo)")
    topic = st.selectbox("Select topic for micro notes:", topics)
    if st.button("Generate Micro Notes"):
        notes = generate_micro_notes(topic)
        st.json(notes)

st.info("Load data and click 'Analyze Performance' to begin.")
