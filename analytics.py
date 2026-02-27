"""
analytics.py
Calculates topic/subject accuracy, failure rates, and time metrics from mock test data.
"""
import sqlite3
from collections import defaultdict
from database import get_connection

def get_topic_performance(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT subject, topic, subtopic, difficulty_level, is_correct, time_taken
        FROM questions
        JOIN mock_tests ON questions.test_id = mock_tests.test_id
        WHERE mock_tests.student_id = ?
    """, (student_id,))
    rows = c.fetchall()
    conn.close()

    topic_stats = defaultdict(lambda: {
        'total': 0, 'correct': 0, 'hard_total': 0, 'hard_wrong': 0, 'time_sum': 0, 'time_count': 0
    })
    subject_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
    all_times = []

    for row in rows:
        subject, topic, subtopic, difficulty, is_correct, time_taken = row
        topic_key = (subject, topic)
        topic_stats[topic_key]['total'] += 1
        topic_stats[topic_key]['time_sum'] += time_taken
        topic_stats[topic_key]['time_count'] += 1
        subject_stats[subject]['total'] += 1
        all_times.append(time_taken)
        if is_correct:
            topic_stats[topic_key]['correct'] += 1
            subject_stats[subject]['correct'] += 1
        if difficulty == 'hard':
            topic_stats[topic_key]['hard_total'] += 1
            if not is_correct:
                topic_stats[topic_key]['hard_wrong'] += 1

    avg_time = sum(all_times) / len(all_times) if all_times else 0
    topic_performance = {}
    for (subject, topic), stats in topic_stats.items():
        accuracy = stats['correct'] / stats['total'] if stats['total'] else 0
        hard_fail_rate = stats['hard_wrong'] / stats['hard_total'] if stats['hard_total'] else 0
        avg_topic_time = stats['time_sum'] / stats['time_count'] if stats['time_count'] else 0
        time_inefficiency = max(0, (avg_topic_time - avg_time) / avg_time) if avg_time else 0
        topic_performance[topic] = {
            'subject': subject,
            'accuracy': round(accuracy, 2),
            'hard_fail_rate': round(hard_fail_rate, 2),
            'avg_time': round(avg_topic_time, 2),
            'time_inefficiency': round(time_inefficiency, 2),
            'total': stats['total']
        }
    subject_performance = {
        subject: {
            'accuracy': round(stats['correct'] / stats['total'], 2) if stats['total'] else 0,
            'total': stats['total']
        } for subject, stats in subject_stats.items()
    }
    return {
        'topic_performance': topic_performance,
        'subject_performance': subject_performance,
        'avg_time': round(avg_time, 2)
    }

if __name__ == "__main__":
    # Demo for student_id=1
    import json
    print(json.dumps(get_topic_performance(1), indent=2))
