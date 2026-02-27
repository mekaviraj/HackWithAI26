from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import logging

# Import modules
from analyzer import PerformanceAnalyzer
from planner import SevenDayPlanner
from recommendations import StudyMaterialRecommender
from genai import generate_study_guidance

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, template_folder='../frontend', static_folder='../frontend/static')
CORS(app)

# Configuration
UPLOAD_FOLDER = '../data'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
logger.info("Flask app initialized successfully")

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
        logger.info("=== Upload request received ===")
        
        if 'file' not in request.files:
            logger.error("No file in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Only CSV files are allowed'}), 400
        
        logger.info(f"Processing file: {file.filename}")
        
        # Read CSV
        df = pd.read_csv(file)
        
        # Validate data
        if df.empty:
            logger.error("CSV file is empty")
            return jsonify({'error': 'CSV file is empty'}), 400
        
        logger.info(f"CSV loaded with {len(df)} rows")
        
        # Perform analysis
        logger.info("Starting performance analysis...")
        analyzer = PerformanceAnalyzer(df)
        analysis = analyzer.analyze()
        logger.info("Analysis complete")
        
        ranked_subtopics = analysis['subtopic_ranking']
        topics = analysis['topics']
        logger.info(f"Ranked subtopics: {[s['subtopic'] for s in ranked_subtopics]}")

        # Generate 7-day plan
        logger.info("Generating 7-day study plan...")
        planner = SevenDayPlanner(ranked_subtopics)
        plan = planner.generate_plan()
        logger.info("Study plan generated")
        
        # Get recommendations
        logger.info("Getting study material recommendations...")
        recommender = StudyMaterialRecommender()
        recommendations = recommender.recommend_materials(ranked_subtopics, topics)
        logger.info(f"Recommendations retrieved: {list(recommendations.keys())}")
        
        study_tips = {}
        for item in ranked_subtopics[:5]:
            topic = item.get('topic', '')
            subtopic = item.get('subtopic', 'Subtopic')
            study_tips[subtopic] = recommender.get_study_tips(topic)
        logger.info("Study tips generated")

        # Optional GenAI override
        logger.info("=== Attempting GenAI call ===")
        genai_payload = generate_study_guidance(analysis, recommendations)
        
        if genai_payload:
            logger.info("✓ GenAI override applied for plan, recommendations, and tips.")
            print("[SUCCESS] GenAI override applied!")
            plan = genai_payload.get('plan', plan)
            recommendations = genai_payload.get('recommendations', recommendations)
            study_tips = genai_payload.get('study_tips', study_tips)
            genai_status = {
                "used": True, 
                "message": "✓ GenAI applied to plan, materials, and tips."
            }
        else:
            logger.warning("GenAI call failed or returned None; falling back to rule-based outputs.")
            print("[WARNING] GenAI not used; falling back to rule-based outputs.")
            genai_status = {
                "used": False, 
                "message": "⚠ GenAI unavailable. Using rule-based outputs."
            }
        
        response_data = {
            'success': True,
            'analysis': analysis,
            'plan': plan,
            'recommendations': recommendations,
            'study_tips': study_tips,
            'genai_status': genai_status
        }
        
        logger.info("=== Response ready to send ===")
        return jsonify(response_data)
    
    except pd.errors.ParserError as e:
        error_msg = f'CSV parsing error: {str(e)}'
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 400
    except Exception as e:
        error_msg = f'Error processing file: {str(e)}'
        logger.error(error_msg, exc_info=True)
        return jsonify({'error': error_msg}), 500

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
        },
        'genai_status': {
            'used': False,
            'message': 'Sample data uses rule-based outputs.'
        }
    }
    return jsonify(sample_data)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
