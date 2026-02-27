import os
from typing import List, Dict

from rag import ResourceRetriever, get_default_resource_path

class StudyMaterialRecommender:
    """Recommends free study materials for weak areas"""
    
    # Free study resources database
    RESOURCES = {
        'math': [
            {'name': 'Khan Academy - Math', 'url': 'https://www.khanacademy.org/math', 'type': 'Video Lessons'},
            {'name': 'Brilliant.org - Math', 'url': 'https://brilliant.org', 'type': 'Interactive Problems'},
            {'name': 'Art of Problem Solving', 'url': 'https://artofproblemsolving.com/wiki', 'type': 'Problem Bank'},
            {'name': 'Mathway', 'url': 'https://www.mathway.com', 'type': 'Solver & Practice'},
        ],
        'physics': [
            {'name': 'Khan Academy - Physics', 'url': 'https://www.khanacademy.org/science/physics', 'type': 'Video Lessons'},
            {'name': 'OpenStax Physics Textbook', 'url': 'https://openstax.org/details/books/college-physics', 'type': 'Free Textbook'},
            {'name': 'Physics Simulation - PhET', 'url': 'https://phet.colorado.edu', 'type': 'Interactive Simulations'},
            {'name': 'Crash Course - Physics', 'url': 'https://www.youtube.com/c/crashcourse', 'type': 'YouTube Series'},
        ],
        'chemistry': [
            {'name': 'Khan Academy - Chemistry', 'url': 'https://www.khanacademy.org/science/chemistry', 'type': 'Video Lessons'},
            {'name': 'OpenStax Chemistry Textbook', 'url': 'https://openstax.org/details/books/chemistry-2e', 'type': 'Free Textbook'},
            {'name': 'Periodic Table Live', 'url': 'https://www.periodicTable.com', 'type': 'Interactive Tool'},
            {'name': 'ChemEdX', 'url': 'https://www.chmedx.org', 'type': 'Experiments & Guides'},
        ],
        'biology': [
            {'name': 'Khan Academy - Biology', 'url': 'https://www.khanacademy.org/science/biology', 'type': 'Video Lessons'},
            {'name': 'OpenStax Biology Textbook', 'url': 'https://openstax.org/details/books/biology-2e', 'type': 'Free Textbook'},
            {'name': 'Amoeba Sisters', 'url': 'https://www.youtube.com/c/AmoebaSisters', 'type': 'YouTube Videos'},
            {'name': 'Bozeman Science', 'url': 'https://www.youtube.com/c/BozemanScience', 'type': 'YouTube Channel'},
        ],
        'english': [
            {'name': 'Grammarly Blog', 'url': 'https://www.grammarly.com/blog', 'type': 'Grammar Tips'},
            {'name': 'Purdue OWL', 'url': 'https://owl.purdue.edu', 'type': 'Writing Resources'},
            {'name': 'Project Gutenberg', 'url': 'https://www.gutenberg.org', 'type': 'Free Books'},
            {'name': 'TED-Ed - English', 'url': 'https://www.youtube.com/user/TEDEd', 'type': 'Educational Videos'},
        ],
        'history': [
            {'name': 'Khan Academy - History', 'url': 'https://www.khanacademy.org/humanities/history', 'type': 'Video Lessons'},
            {'name': 'Crash Course - History', 'url': 'https://www.youtube.com/c/CrashCourse', 'type': 'YouTube Series'},
            {'name': 'History Channel', 'url': 'https://www.historychannel.com', 'type': 'Documentary Content'},
            {'name': 'Stanford History Education Group', 'url': 'https://sheg.stanford.edu', 'type': 'Teaching Materials'},
        ],
        'geography': [
            {'name': 'Khan Academy - Geography', 'url': 'https://www.khanacademy.org', 'type': 'Video Lessons'},
            {'name': 'Google Earth', 'url': 'https://earth.google.com', 'type': 'Interactive Map'},
            {'name': 'National Geographic', 'url': 'https://www.nationalgeographic.com', 'type': 'Articles & Videos'},
            {'name': 'Map Quiz', 'url': 'https://www.sporcle.com/games/geography', 'type': 'Practice Quizzes'},
        ],
        'science': [
            {'name': 'Khan Academy - Science', 'url': 'https://www.khanacademy.org/science', 'type': 'Comprehensive Science'},
            {'name': 'Crash Course - Science', 'url': 'https://www.youtube.com/c/CrashCourse', 'type': 'Video Series'},
            {'name': 'TED-Ed', 'url': 'https://www.youtube.com/user/TEDEd', 'type': 'Educational Videos'},
            {'name': 'MIT OpenCourseWare', 'url': 'https://ocw.mit.edu', 'type': 'University Courses'},
        ]
    }
    
    def __init__(self) -> None:
        self.retriever = None
        resource_path = get_default_resource_path()
        if os.path.exists(resource_path):
            self.retriever = ResourceRetriever.from_file(resource_path)

    def recommend_materials(self, ranked_subtopics: List[Dict], topics: List[str]) -> Dict:
        """Generate study material recommendations for weak subtopics"""
        recommendations = {}

        # Map subtopics to their topics, fallback to available topics
        for item in ranked_subtopics[:5]:
            topic = item.get("topic", "").lower()
            subtopic = item.get("subtopic", "Subtopic")

            resources = self._rag_recommendations(topic, subtopic)
            recommendations[subtopic] = resources

        return recommendations

    def _rag_recommendations(self, topic: str, subtopic: str) -> List[Dict]:
        if not self.retriever:
            return []
        return self.retriever.retrieve(topic=topic, subtopic=subtopic, top_k=3)

    def get_study_tips(self, subject: str) -> List[str]:
        """Get specific study tips for a subject"""
        tips_by_subject = {
            'math': [
                'Practice problems daily, start with easy ones',
                'Focus on understanding concepts before memorizing formulas',
                'Create formula sheets and concept maps',
                'Use online calculators to verify answers'
            ],
            'physics': [
                'Draw diagrams for each problem',
                'Link concepts to real-world examples',
                'Use simulation software to visualize concepts',
                'Work through step-by-step solutions'
            ],
            'chemistry': [
                'Memorize periodic table basics',
                'Practice balancing chemical equations',
                'Use mnemonics for complex reactions',
                'Create concept flow charts'
            ],
            'biology': [
                'Create detailed diagrams of biological systems',
                'Use flashcards for terminology',
                'Watch animations and videos of processes',
                'Relate concepts to your body'
            ],
            'english': [
                'Read high-quality literature regularly',
                'Practice writing essays daily',
                'Use grammar checking tools',
                'Read peer feedback carefully'
            ]
        }
        
        subject_lower = subject.lower()
        return tips_by_subject.get(subject_lower, [
            'Break the subject into smaller topics',
            'Practice regularly with varied resources',
            'Join study groups or discussion forums',
            'Teach concepts to others'
        ])
