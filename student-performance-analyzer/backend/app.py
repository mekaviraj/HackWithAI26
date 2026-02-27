from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import logging
import sqlite3
import csv

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

def build_revision_summary(analysis):
    summary = analysis.get('summary', {})
    ranked_subtopics = analysis.get('subtopic_ranking', [])

    overall_accuracy = float(summary.get('overall_accuracy', 0.0))
    total_attempts = int(summary.get('total_attempts', 0))

    high_weightage_weak = [
        item for item in ranked_subtopics
        if item.get('topic_weightage') == 'high'
    ][:2]
    low_weightage_weak = [
        item for item in ranked_subtopics
        if item.get('topic_weightage') == 'low'
    ][:2]

    high_names = ', '.join([item.get('subtopic', 'N/A') for item in high_weightage_weak])
    low_names = ', '.join([item.get('subtopic', 'N/A') for item in low_weightage_weak])

    if not high_names:
        high_names = 'no major high-weightage weak chapter detected'
    if not low_names:
        low_names = 'no major low-weightage weak chapter detected'

    possible_gain = max(5, min(20, int((100 - overall_accuracy) * 0.35)))

    return (
        f"The test shows an overall accuracy of {overall_accuracy:.1f}% across {total_attempts} attempts. "
        f"The most important weak areas are {high_names}; these should be your first revision priority because they carry higher weightage and have direct impact on marks. "
        f"Secondary weak areas include {low_names}, which should be covered after stabilizing high-weightage chapters. "
        f"With focused practice on the priority chapters and error correction in the 7-day plan, you can realistically improve by around {possible_gain}% in score."
    )

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
        prioritized_topics = analysis.get('prioritized_topics', [])
        topics = analysis['topics']
        logger.info(f"Ranked subtopics: {[s['subtopic'] for s in ranked_subtopics]}")

        # Generate 7-day plan
        logger.info("Generating 7-day study plan...")
        planner = SevenDayPlanner(ranked_subtopics, prioritized_topics)
        plan = planner.generate_plan()
        logger.info("Study plan generated")
        
        # Get recommendations
        logger.info("Getting study material recommendations...")
        recommender = StudyMaterialRecommender()
        recommendations = recommender.recommend_materials(ranked_subtopics, topics)
        logger.info(f"Recommendations retrieved: {list(recommendations.keys())}")
        
        study_tips = {}
        for item in ranked_subtopics[:5]:
            subtopic = item.get('subtopic', 'Subtopic')
            study_tips[subtopic] = recommender.get_subtopic_study_tips(item)
        logger.info("Study tips generated")

        revision_summary = build_revision_summary(analysis)

        # Optional GenAI override
        use_genai = os.getenv("USE_GENAI", "false").strip().lower() == "true"
        genai_payload = None
        if use_genai:
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
            logger.warning("GenAI disabled/failed; using dynamic rule-based outputs.")
            print("[WARNING] GenAI not used; using dynamic rule-based outputs.")
            genai_status = {
                "used": False, 
                "message": "Using dynamic rule-based outputs."
            }
        
        response_data = {
            'success': True,
            'analysis': analysis,
            'plan': plan,
            'recommendations': recommendations,
            'study_tips': study_tips,
            'revision_summary': revision_summary,
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
    """Get sample analysis data from current sample CSV using real pipeline logic"""
    try:
        df = pd.read_csv('../data/sample_data.csv')
        if df.empty:
            return jsonify({'error': 'Sample CSV is empty'}), 400

        analyzer = PerformanceAnalyzer(df)
        analysis = analyzer.analyze()

        ranked_subtopics = analysis['subtopic_ranking']
        prioritized_topics = analysis.get('prioritized_topics', [])
        topics = analysis['topics']

        planner = SevenDayPlanner(ranked_subtopics, prioritized_topics)
        plan = planner.generate_plan()

        recommender = StudyMaterialRecommender()
        recommendations = recommender.recommend_materials(ranked_subtopics, topics)

        study_tips = {}
        for item in ranked_subtopics[:5]:
            subtopic = item.get('subtopic', 'Subtopic')
            study_tips[subtopic] = recommender.get_subtopic_study_tips(item)

        revision_summary = build_revision_summary(analysis)

        return jsonify({
            'success': True,
            'analysis': analysis,
            'plan': plan,
            'recommendations': recommendations,
            'study_tips': study_tips,
            'revision_summary': revision_summary,
            'genai_status': {
                'used': False,
                'message': 'Sample data generated dynamically from sample CSV.'
            }
        })
    except Exception as e:
        logger.error(f"Error generating sample data: {e}", exc_info=True)
        return jsonify({'error': f'Error generating sample data: {str(e)}'}), 500
# --------------------------------------------------
# DATABASE INITIALIZATION (ADDED)
# --------------------------------------------------
def init_db():
    conn = sqlite3.connect('student.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            question_id TEXT PRIMARY KEY,
            test_id TEXT,
            subject TEXT,
            topic TEXT,
            subtopic TEXT,
            difficulty_level TEXT,
            is_correct INTEGER,
            time_taken INTEGER,
            topic_weightage TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def load_sample_data(csv_path='../data/sample_data.csv'):
    conn = sqlite3.connect('student.db')
    c = conn.cursor()

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if not row.get('question_id'):
                continue

            c.execute('''
                INSERT OR REPLACE INTO questions (
                    question_id,
                    test_id,
                    subject,
                    topic,
                    subtopic,
                    difficulty_level,
                    is_correct,
                    time_taken,
                    topic_weightage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row.get('question_id'),
                row.get('test_id'),
                row.get('subject'),
                row.get('topic'),
                row.get('subtopic'),
                row.get('difficulty_level'),
                int(row.get('is_correct', 0)),
                int(row.get('time_taken', 0)),
                (row.get('topic_weightage') or 'low').strip().lower(),
            ))

    conn.commit()
    conn.close()
    logger.info("Sample data loaded successfully")
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    init_db()
    load_sample_data()
    app.run(debug=True, port=5000)