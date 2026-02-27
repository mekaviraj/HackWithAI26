from typing import List, Dict
from datetime import datetime, timedelta

class SevenDayPlanner:
    """Generates a 7-day problem-focused study plan"""

    def __init__(self, ranked_subtopics: List[Dict], prioritized_topics: List[Dict] = None):
        self.ranked_subtopics = ranked_subtopics
        self.prioritized_topics = prioritized_topics or []
        self.start_date = datetime.now()
    
    def generate_plan(self) -> List[Dict]:
        """Generate a 7-day plan focusing on weakest areas"""
        focus_areas = self.ranked_subtopics[:3]
        if not focus_areas:
            return self._default_plan()

        allocations = self._allocate_days(focus_areas)
        plan = []
        day_num = 1

        for item, days in allocations:
            for _ in range(days):
                if day_num > 6:
                    break
                current_date = self.start_date + timedelta(days=day_num - 1)
                subtopic = item.get('subtopic', 'Focus Area')
                plan.append({
                    'day': day_num,
                    'date': current_date.strftime('%Y-%m-%d'),
                    'focus': [subtopic],
                    'study_time': self._study_time_for(item),
                    'activities': self._get_activities_for_item(item, day_num),
                    'goals': self._get_goals_for_item(item),
                })
                day_num += 1

        while day_num <= 6:
            current_date = self.start_date + timedelta(days=day_num - 1)
            plan.append({
                'day': day_num,
                'date': current_date.strftime('%Y-%m-%d'),
                'focus': ['Targeted Mixed Practice'],
                'study_time': '2 hours',
                'activities': [
                    '🧪 Mixed practice from weak subtopics',
                    '📝 Timed question set (20-30 minutes)',
                    '📘 Error log review and corrections'
                ],
                'goals': [
                    'Reduce repeated mistakes in weak areas',
                    'Improve speed without losing accuracy'
                ],
            })
            day_num += 1

        revision_focus = [item.get('subtopic', 'Revision') for item in focus_areas]
        revision_date = self.start_date + timedelta(days=6)
        plan.append({
            'day': 7,
            'date': revision_date.strftime('%Y-%m-%d'),
            'focus': revision_focus,
            'study_time': '3 hours',
            'activities': [
                '📝 Full revision of top weak subtopics',
                '🎯 Full mock test under exam conditions',
                '📊 Analyze errors and make final fix list'
            ],
            'goals': [
                'Reach target accuracy in all priority weak areas',
                'Be exam-ready for high-weightage topics'
            ],
        })

        return plan

    def generate_revision_plan(self, prioritized_topics: List[Dict]) -> List[Dict]:
        plan = []
        day = 1

        for item in prioritized_topics[:3]:
            topic = item.get('topic', 'Topic')
            weightage = item.get('weightage', 'low')
            difficulty = item.get('difficulty', 'easy')
            days_alloc = 3 if weightage == 'high' and difficulty == 'hard' else 2

            for _ in range(days_alloc):
                if day > 6:
                    break
                current_date = self.start_date + timedelta(days=day-1)
                focus_topics = [topic]
                plan.append({
                    'day': day,
                    'date': current_date.strftime('%Y-%m-%d'),
                    'focus': focus_topics,
                    'study_time': '2-3 hours',
                    'activities': self._get_activities(focus_topics, day),
                    'goals': self._get_daily_goals(focus_topics)
                })
                day += 1

            if day > 6:
                break

        while day <= 6:
            current_date = self.start_date + timedelta(days=day-1)
            focus_topics = ['Targeted Practice']
            plan.append({
                'day': day,
                'date': current_date.strftime('%Y-%m-%d'),
                'focus': focus_topics,
                'study_time': '2-3 hours',
                'activities': self._get_activities(focus_topics, day),
                'goals': self._get_daily_goals(focus_topics)
            })
            day += 1

        revision_focus = [item.get('topic', 'Topic') for item in prioritized_topics[:3]]
        if not revision_focus:
            revision_focus = ['Full Revision/Mock']
        revision_date = self.start_date + timedelta(days=6)
        plan.append({
            'day': 7,
            'date': revision_date.strftime('%Y-%m-%d'),
            'focus': revision_focus,
            'study_time': '3 hours',
            'activities': self._get_activities(revision_focus, 7),
            'goals': self._get_daily_goals(revision_focus)
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

        focus = topics[0] if topics else "focus area"
        cycle = day % 3

        if cycle == 1:
            activities = [
                f'📚 Study core concepts of {focus}',
                f'✍️ Solve 10-15 foundational problems in {focus}',
                f'🎯 Attempt 3-5 exam-style questions from {focus}'
            ]
        elif cycle == 2:
            activities = [
                f'📘 Review key formulas and shortcuts for {focus}',
                f'🧪 Solve mixed-level practice set on {focus}',
                f'📝 Analyze mistakes and retry missed {focus} questions'
            ]
        else:
            activities = [
                f'🔁 Rapid recap of {focus} notes and concepts',
                f'⏱️ Timed practice block for {focus} (20-25 mins)',
                f'🎯 Apply {focus} in previous-year style questions'
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

    def _default_plan(self) -> List[Dict]:
        plan = []
        for day in range(1, 8):
            current_date = self.start_date + timedelta(days=day - 1)
            plan.append({
                'day': day,
                'date': current_date.strftime('%Y-%m-%d'),
                'focus': ['General Revision'],
                'study_time': '2 hours',
                'activities': ['📚 Review notes', '🧪 Solve practice set'],
                'goals': ['Maintain consistency and improve confidence'],
            })
        return plan

    def _severity_score(self, item: Dict) -> float:
        accuracy = float(item.get('accuracy', 0))
        mistakes = int(item.get('mistakes', 0))
        weightage = item.get('topic_weightage', 'low')
        difficulty = item.get('difficulty', 'easy')
        slow_penalty = float(item.get('avg_time_incorrect', 0)) / 25

        return (
            (100 - accuracy)
            + (mistakes * 10)
            + (12 if weightage == 'high' else 0)
            + (8 if difficulty == 'hard' else 0)
            + slow_penalty
        )

    def _allocate_days(self, focus_areas: List[Dict]) -> List:
        scored = sorted(
            [(item, self._severity_score(item)) for item in focus_areas],
            key=lambda x: x[1],
            reverse=True,
        )

        if len(scored) == 1:
            return [(scored[0][0], 6)]
        if len(scored) == 2:
            return [(scored[0][0], 4), (scored[1][0], 2)]
        return [(scored[0][0], 3), (scored[1][0], 2), (scored[2][0], 1)]

    def _study_time_for(self, item: Dict) -> str:
        if item.get('topic_weightage') == 'high' and item.get('difficulty') == 'hard':
            return '2.5-3 hours'
        if float(item.get('accuracy', 0)) < 50:
            return '2-2.5 hours'
        return '2 hours'

    def _get_activities_for_item(self, item: Dict, day: int) -> List[str]:
        subtopic = item.get('subtopic', 'focus area')
        day_variant = day % 3
        if day_variant == 1:
            activities = [
                f'📚 Concept rebuild session for {subtopic}',
                f'✍️ Guided starter set on {subtopic}',
            ]
        elif day_variant == 2:
            activities = [
                f'🎯 Application-focused problems for {subtopic}',
                f'🧠 Formula/recall drill for {subtopic}',
            ]
        else:
            activities = [
                f'📝 Error-correction worksheet for {subtopic}',
                f'🔁 Mixed revision quiz on {subtopic}',
            ]

        if float(item.get('avg_time_incorrect', 0)) > 90:
            activities.append('⏱️ Timed drill: 10-12 questions in 25 minutes')
        else:
            activities.append('🎯 Concept + application mix (8-10 questions)')
        if day % 2 == 0:
            activities.append('📋 Mini quiz and error review')
        return activities

    def _get_goals_for_item(self, item: Dict) -> List[str]:
        subtopic = item.get('subtopic', 'focus area')
        current_accuracy = float(item.get('accuracy', 0))
        target_accuracy = min(95, int(current_accuracy + 15))
        goals = [
            f'Increase {subtopic} accuracy from {current_accuracy:.1f}% to {target_accuracy}%+',
            f'Reduce mistakes in {subtopic} through focused correction',
        ]
        if float(item.get('avg_time_incorrect', 0)) > 90:
            goals.append(f'Reduce average wrong-attempt time in {subtopic} by at least 15%.')
        return goals
