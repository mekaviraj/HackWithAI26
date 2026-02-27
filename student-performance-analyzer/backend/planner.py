from typing import List, Dict
from datetime import datetime, timedelta

class SevenDayPlanner:
    """Generates a 7-day problem-focused study plan"""

    def __init__(self, ranked_subtopics: List[Dict]):
        self.ranked_subtopics = ranked_subtopics
        self.start_date = datetime.now()
    
    def generate_plan(self) -> List[Dict]:
        """Generate a 7-day plan focusing on weakest areas"""
        plan = []
        
        # Get top 5 weak subtopics (or fewer if less available)
        focus_areas = self.ranked_subtopics[:5]
        
        # Distribute topics across 7 days
        day_topics = self._distribute_topics(focus_areas)
        
        for day_num in range(1, 8):
            topics = day_topics.get(day_num, [])
            current_date = self.start_date + timedelta(days=day_num-1)
            
            plan.append({
                'day': day_num,
                'date': current_date.strftime('%Y-%m-%d'),
                'focus': topics,
                'study_time': '2-3 hours',
                'activities': self._get_activities(topics, day_num),
                'goals': self._get_daily_goals(topics)
            })
        
        return plan
    
    def _distribute_topics(self, focus_areas: List[Dict]) -> Dict:
        """Distribute weak subtopics across 7 days"""
        distribution = {}
        total_areas = len(focus_areas)
        
        # Day 1-2: Strongest focus on weakest area
        # Day 3-4: Second weakest area
        # Day 5-6: Remaining areas
        # Day 7: Revision
        
        if total_areas >= 1:
            distribution[1] = [focus_areas[0]['subtopic']]
            distribution[2] = [focus_areas[0]['subtopic']]
        
        if total_areas >= 2:
            distribution[3] = [focus_areas[1]['subtopic']]
            distribution[4] = [focus_areas[1]['subtopic']]
        
        if total_areas >= 3:
            distribution[5] = [focus_areas[2]['subtopic']]
        
        if total_areas >= 4:
            distribution[6] = [focus_areas[3]['subtopic']]
        
        # Day 7 revision
        distribution[7] = [focus_areas[i]['subtopic'] for i in range(min(3, total_areas))]
        
        return distribution
    
    def _get_activities(self, topics: List, day: int) -> List[str]:
        """Get recommended activities for each day"""
        if day == 7:
            return [
                '📝 Quick revision of all topics',
                '🧪 Practice tests from previous days',
                '📊 Self-assessment and evaluation'
            ]
        
        activities = [
            f'📚 Study core concepts of {topics[0] if topics else "focus area"}',
            '✍️ Solve 10-15 practice problems',
            '🎯 Attempt mock questions'
        ]
        
        if day % 2 == 0:
            activities.append('📋 Take a short quiz')
        
        return activities
    
    def _get_daily_goals(self, topics: List) -> List[str]:
        """Get daily learning goals"""
        if not topics:
            return ['Complete revision objectives']
        
        subject = topics[0]
        return [
            f'Understand key concepts in {subject}',
            f'Practice at least 10 questions in {subject}',
            f'Identify remaining weak points in {subject}',
            'Aim for 70%+ accuracy in practice'
        ]
