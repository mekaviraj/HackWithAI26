#!/usr/bin/env python
"""Test GenAI integration"""

import sys
import json
import requests
from genai import generate_study_guidance

# Test data
test_analysis = {
    "summary": {
        "total_attempts": 24,
        "overall_accuracy": 62.5,
        "avg_time_correct": 42.8,
        "avg_time_incorrect": 61.3,
        "strength_level": "Developing",
    },
    "accuracy_by_difficulty": [
        {"difficulty": 1, "accuracy": 80.0, "attempts": 8},
        {"difficulty": 2, "accuracy": 60.0, "attempts": 10},
        {"difficulty": 3, "accuracy": 42.9, "attempts": 6}
    ],
    "time_comparison": {
        "avg_time_correct": 42.8,
        "avg_time_incorrect": 61.3
    },
    "subtopic_ranking": [
        {"subtopic": "Newton's Laws of Motion", "topic": "Physics", "accuracy": 50.0, "attempts": 8},
        {"subtopic": "Kinematics", "topic": "Physics", "accuracy": 62.5, "attempts": 8},
        {"subtopic": "Work and Energy", "topic": "Physics", "accuracy": 75.0, "attempts": 8}
    ],
    "topics": ["Physics"]
}

test_recommendations = {
    "Newton's Laws of Motion": [
        {
            "name": "Khan Academy - Forces and Newton's Laws",
            "url": "https://www.khanacademy.org/science/physics/forces-newtons-laws",
            "type": "Video Lessons"
        },
        {
            "name": "PhET - Forces and Motion",
            "url": "https://phet.colorado.edu/en/simulation/forces-and-motion-basics",
            "type": "Interactive Simulation"
        }
    ]
}

print("=" * 60)
print("Testing GenAI Integration")
print("=" * 60)

try:
    print("\n[1] Calling generate_study_guidance()...")
    result = generate_study_guidance(test_analysis, test_recommendations)
    
    if result:
        print("\n[✓] SUCCESS! GenAI returned valid response")
        print(f"\nResponse keys: {list(result.keys())}")
        print(f"Plan days: {len(result.get('plan', []))}")
        print(f"Recommendations: {len(result.get('recommendations', {}))}")
        print(f"Study tips: {len(result.get('study_tips', {}))}")
        print("\nFirst day of plan:")
        first_day = result.get('plan', [{}])[0]
        print(json.dumps(first_day, indent=2)[:300])
    else:
        print("\n[✗] FAILED! GenAI returned None")
        print("Check the logs above for error details")
        
except Exception as e:
    print(f"\n[✗] EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
