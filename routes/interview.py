from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from backend.services.interview import generate_interview_questions, evaluate_interview_answer
from backend.services.chat import ask_career_coach

interview_bp = Blueprint('interview', __name__)

@interview_bp.route('/interview/questions', methods=['POST'])
@jwt_required()
def get_questions():
    data = request.get_json() or {}
    matched_skills = data.get('matched_skills', [])
    missing_skills = data.get('missing_skills', [])
    jd_text = data.get('jd_text', "")
    
    api_key = current_app.config.get('GEMINI_API_KEY')
    
    try:
        questions = generate_interview_questions(
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            jd_text=jd_text,
            api_key=api_key
        )
        return jsonify(questions), 200
    except Exception as e:
        return jsonify({"error": f"Failed to generate questions: {str(e)}"}), 500

@interview_bp.route('/interview/evaluate', methods=['POST'])
@jwt_required()
def evaluate_answer():
    data = request.get_json() or {}
    question = data.get('question')
    answer = data.get('answer')
    jd_text = data.get('jd_text', '')
    
    if not question or not answer:
        return jsonify({"error": "question and answer are required"}), 400
        
    api_key = current_app.config.get('GEMINI_API_KEY')
    
    try:
        evaluation = evaluate_interview_answer(
            question=question,
            user_answer=answer,
            jd_text=jd_text,
            api_key=api_key
        )
        return jsonify(evaluation), 200
    except Exception as e:
        return jsonify({"error": f"Failed to evaluate response: {str(e)}"}), 500

@interview_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    data = request.get_json() or {}
    query = data.get('query')
    resume_text = data.get('resume_text', '')
    jd_text = data.get('jd_text', '')
    chat_history = data.get('chat_history', [])
    
    if not query:
        return jsonify({"error": "query is required"}), 400
        
    api_key = current_app.config.get('GEMINI_API_KEY')
    
    try:
        response_text = ask_career_coach(
            query=query,
            resume_text=resume_text,
            jd_text=jd_text,
            history_list=chat_history, # Pass history list
            api_key=api_key
        )
        return jsonify({"response": response_text}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to query career coach: {str(e)}"}), 500
