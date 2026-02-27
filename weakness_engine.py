"""
weakness_engine.py
Ranks topics by weakness score using rule-based formula.
"""

def compute_weakness_scores(topic_performance, w1=0.5, w2=0.3, w3=0.2):
    """
    topic_performance: dict from analytics.py
    Returns: list of dicts [{topic, weakness_score}]
    """
    scores = []
    for topic, perf in topic_performance.items():
        score = (
            (1 - perf['accuracy']) * w1 +
            perf['hard_fail_rate'] * w2 +
            perf['time_inefficiency'] * w3
        )
        scores.append({
            'topic': topic,
            'weakness_score': round(score, 2)
        })
    # Sort descending
    scores.sort(key=lambda x: x['weakness_score'], reverse=True)
    return scores

def get_top_weak_topics(topic_performance, top_n=3):
    scores = compute_weakness_scores(topic_performance)
    return {'weak_topics': scores[:top_n]}

if __name__ == "__main__":
    # Demo
    sample = {
        'Calculus': {'accuracy': 0.4, 'hard_fail_rate': 0.8, 'time_inefficiency': 0.5},
        'Algebra': {'accuracy': 0.7, 'hard_fail_rate': 0.2, 'time_inefficiency': 0.1},
        'Probability': {'accuracy': 0.5, 'hard_fail_rate': 0.6, 'time_inefficiency': 0.3}
    }
    print(get_top_weak_topics(sample))
