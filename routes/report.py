from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import io
from backend.models.database import db
from backend.models.report import AnalysisReport
from backend.models.resume import Resume
from backend.services.report import generate_pdf_report

report_bp = Blueprint('report', __name__)

@report_bp.route('/report', methods=['POST'])
@jwt_required()
def create_report():
    """
    Endpoint: POST /report
    Generates and downloads a PDF report for a given analysis report ID.
    """
    data = request.get_json() or {}
    report_id = data.get('report_id')
    
    if not report_id:
        return jsonify({"error": "report_id is required"}), 400
        
    user_id = get_jwt_identity()
    
    # Query report ensuring it belongs to this user's resume
    report = AnalysisReport.query.join(Resume).filter(
        AnalysisReport.id == report_id,
        Resume.user_id == int(user_id)
    ).first()
    
    if not report:
        return jsonify({"error": "Report not found"}), 404
        
    try:
        # Prepare report data dict
        report_data = {
            "filename": report.resume.filename if report.resume else "Resume",
            "overall_score": report.overall_score,
            "breakdown": report.get_breakdown(),
            "matched_skills": report.get_matched_skills(),
            "missing_skills": report.get_missing_skills(),
            "suggestions": report.get_suggestions(),
            "interview_questions": report.get_interview_questions()
        }
        
        pdf_bytes = generate_pdf_report(report_data)
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"PRO_ALIGN_Report_{report_id}.pdf"
        )
    except Exception as e:
        return jsonify({"error": f"Failed to generate report PDF: {str(e)}"}), 500

@report_bp.route('/report/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """
    Endpoint: DELETE /report/<id>
    """
    user_id = get_jwt_identity()
    
    # Query report ensuring it belongs to this user
    report = AnalysisReport.query.join(Resume).filter(
        AnalysisReport.id == report_id,
        Resume.user_id == int(user_id)
    ).first()
    
    if not report:
        return jsonify({"error": "Report not found or unauthorized"}), 404
        
    try:
        db.session.delete(report)
        db.session.commit()
        return jsonify({"message": "Report deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete report: {str(e)}"}), 500
