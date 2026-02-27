"""
planner.py
Generates a 7-day revision plan allocation based on weak topics.
"""

def allocate_7_day_plan(weak_topics):
    """
    weak_topics: list of dicts [{topic, weakness_score}]
    Returns: dict with day-topic allocation
    """
    plan = {}
    topics = [wt['topic'] for wt in weak_topics]
    plan['day_1'] = {'topic': topics[0], 'type': 'theory+practice', 'minutes': 120}
    plan['day_2'] = {'topic': topics[0], 'type': 'practice', 'minutes': 60}
    plan['day_3'] = {'topic': topics[0], 'type': 'theory', 'minutes': 60}
    if len(topics) > 1:
        plan['day_4'] = {'topic': topics[1], 'type': 'theory+practice', 'minutes': 90}
        plan['day_5'] = {'topic': topics[1], 'type': 'practice', 'minutes': 60}
    if len(topics) > 2:
        plan['day_6'] = {'topic': topics[2], 'type': 'theory+practice', 'minutes': 90}
    plan['day_7'] = {'topic': 'Full Revision/Mock', 'type': 'mock', 'minutes': 180}
    return plan

if __name__ == "__main__":
    # Demo
    weak_topics = [
        {'topic': 'Calculus', 'weakness_score': 0.74},
        {'topic': 'Probability', 'weakness_score': 0.63},
        {'topic': 'Algebra', 'weakness_score': 0.55}
    ]
    import json
    print(json.dumps(allocate_7_day_plan(weak_topics), indent=2))
