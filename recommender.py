"""
recommender.py
Recommends study materials for weak topics from the database.
"""
import sqlite3
from database import get_connection

def get_study_materials_for_topic(topic, failed_difficulty=None):
    conn = get_connection()
    c = conn.cursor()
    # Prefer easier than failed difficulty
    diff_order = ['easy', 'medium', 'hard']
    if failed_difficulty and failed_difficulty in diff_order:
        idx = diff_order.index(failed_difficulty)
        allowed = diff_order[:max(idx, 1)]  # at least 'easy' if failed 'easy'
    else:
        allowed = diff_order
    materials = {}
    for rtype in ['video', 'notes', 'practice']:
        c.execute('''SELECT resource_title, resource_link_or_text, estimated_time, difficulty_level FROM study_material
                     WHERE topic=? AND resource_type=? AND difficulty_level IN ({})
                     ORDER BY difficulty_level ASC LIMIT 1'''.format(
            ','.join(['?']*len(allowed))), [topic, rtype] + allowed)
        row = c.fetchone()
        if row:
            materials[rtype] = {
                'title': row[0],
                'link_or_text': row[1],
                'estimated_time': row[2],
                'difficulty_level': row[3]
            }
    conn.close()
    return materials

def recommend_for_weak_topics(weak_topics):
    recs = {}
    for wt in weak_topics:
        topic = wt['topic']
        recs[topic] = get_study_materials_for_topic(topic)
    return recs

if __name__ == "__main__":
    # Demo
    print(recommend_for_weak_topics([
        {'topic': 'Calculus'},
        {'topic': 'Probability'}
    ]))
