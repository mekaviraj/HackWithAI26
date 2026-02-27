from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from analyzer import PerformanceAnalyzer
from planner import SevenDayPlanner
from recommendations import StudyMaterialRecommender

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend/static')
CORS(app)

# Configuration
UPLOAD_FOLDER = '../data'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Serve the dashboard"""
    return render_template('dashboard.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only CSV files are allowed'}), 400
        
        # Read CSV
        df = pd.read_csv(file)
        
        # Validate data
        if df.empty:
            return jsonify({'error': 'CSV file is empty'}), 400
        
        # Perform analysis
        analyzer = PerformanceAnalyzer(df)
        analysis = analyzer.analyze()
        
        ranked_subtopics = analysis['subtopic_ranking']
        topics = analysis['topics']

        # Generate 7-day plan
        planner = SevenDayPlanner(ranked_subtopics)
        plan = planner.generate_plan()
        
        # Get recommendations
        recommender = StudyMaterialRecommender()
        recommendations = recommender.recommend_materials(ranked_subtopics, topics)
        study_tips = {}
        for item in ranked_subtopics[:5]:
            topic = item.get('topic', '')
            subtopic = item.get('subtopic', 'Subtopic')
            study_tips[subtopic] = recommender.get_study_tips(topic)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'plan': plan,
            'recommendations': recommendations,
            'study_tips': study_tips
        })
    
    except pd.errors.ParserError as e:
        return jsonify({'error': f'CSV parsing error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/api/sample', methods=['GET'])
def get_sample_data():
    """Get sample analysis data for demo"""
    sample_data = {
        'analysis': {
            'summary': {
                'total_attempts': 24,
                'overall_accuracy': 62.5,
                'avg_time_correct': 42.8,
                'avg_time_incorrect': 61.3,
                'strength_level': 'Developing'
            },
            'accuracy_by_difficulty': [
                {'difficulty': 1, 'accuracy': 80.0, 'attempts': 8},
                {'difficulty': 2, 'accuracy': 60.0, 'attempts': 10},
                {'difficulty': 3, 'accuracy': 42.9, 'attempts': 6}
            ],
            'time_comparison': {
                'avg_time_correct': 42.8,
                'avg_time_incorrect': 61.3
            },
            'strength_progression': [
                {'test_id': 'Test 1', 'strength_score': 55.1},
                {'test_id': 'Test 2', 'strength_score': 61.2}
            ],
            'subtopic_ranking': [
                {'subtopic': "Newton's Laws of Motion", 'topic': 'Physics', 'accuracy': 50.0, 'attempts': 8},
                {'subtopic': 'Kinematics', 'topic': 'Physics', 'accuracy': 62.5, 'attempts': 8},
                {'subtopic': 'Work and Energy', 'topic': 'Physics', 'accuracy': 75.0, 'attempts': 8}
            ],
            'topics': ['Physics']
        },
        'plan': [
            {
                'day': 1,
                'date': '2026-02-27',
                'focus': ["Newton's Laws of Motion"],
                'study_time': '2-3 hours',
                'activities': ["📚 Study core concepts of Newton's Laws of Motion", '✍️ Solve 10-15 practice problems', '🎯 Attempt mock questions'],
                'goals': ["Understand key concepts in Newton's Laws of Motion", "Practice at least 10 questions in Newton's Laws of Motion", "Identify remaining weak points in Newton's Laws of Motion", 'Aim for 70%+ accuracy in practice']
            },
            {
                'day': 2,
                'date': '2026-02-28',
                'focus': ["Newton's Laws of Motion"],
                'study_time': '2-3 hours',
                'activities': ["📚 Study core concepts of Newton's Laws of Motion", '✍️ Solve 10-15 practice problems', '🎯 Attempt mock questions', '📋 Take a short quiz'],
                'goals': ["Understand key concepts in Newton's Laws of Motion", "Practice at least 10 questions in Newton's Laws of Motion", "Identify remaining weak points in Newton's Laws of Motion", 'Aim for 70%+ accuracy in practice']
            }
        ],
        'recommendations': {
            "Newton's Laws of Motion": [
                {'name': 'Khan Academy - Physics', 'url': 'https://www.khanacademy.org/science/physics', 'type': 'Video Lessons'},
                {'name': 'OpenStax Physics Textbook', 'url': 'https://openstax.org/details/books/college-physics', 'type': 'Free Textbook'},
                {'name': 'Physics Simulation - PhET', 'url': 'https://phet.colorado.edu', 'type': 'Interactive Simulations'}
            ]
        },
        'study_tips': {
            "Newton's Laws of Motion": ['Draw diagrams for each problem', 'Link concepts to real-world examples', 'Use simulation software to visualize concepts']
        }
    }
    return jsonify(sample_data)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
