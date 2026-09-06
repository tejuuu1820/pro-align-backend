from datetime import datetime
from backend.models.database import db
import json

class AnalysisReport(db.Model):
    __tablename__ = 'analysis_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    
    jd_text = db.Column(db.Text, nullable=False)
    overall_score = db.Column(db.Integer, nullable=False)
    
    # Store scores breakdown JSON
    # (skills, experience, education, semantic, keywords)
    breakdown_json = db.Column(db.Text, nullable=False, default="{}")
    
    # Store lists of matched/missing tags
    matched_skills_json = db.Column(db.Text, nullable=False, default="[]")
    missing_skills_json = db.Column(db.Text, nullable=False, default="[]")
    
    # Store optimizations and interview questions JSON
    suggestions_json = db.Column(db.Text, nullable=False, default="[]")
    interview_questions_json = db.Column(db.Text, nullable=False, default="[]")
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_breakdown(self):
        return json.loads(self.breakdown_json) if self.breakdown_json else {}

    def set_breakdown(self, data):
        self.breakdown_json = json.dumps(data)

    def get_matched_skills(self):
        return json.loads(self.matched_skills_json) if self.matched_skills_json else []

    def set_matched_skills(self, data):
        self.matched_skills_json = json.dumps(data)

    def get_missing_skills(self):
        return json.loads(self.missing_skills_json) if self.missing_skills_json else []

    def set_missing_skills(self, data):
        self.missing_skills_json = json.dumps(data)

    def get_suggestions(self):
        return json.loads(self.suggestions_json) if self.suggestions_json else []

    def set_suggestions(self, data):
        self.suggestions_json = json.dumps(data)

    def get_interview_questions(self):
        return json.loads(self.interview_questions_json) if self.interview_questions_json else []

    def set_interview_questions(self, data):
        self.interview_questions_json = json.dumps(data)

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "filename": self.resume.filename if self.resume else "Unknown",
            "resume": {
                "id": self.resume_id,
                "filename": self.resume.filename if self.resume else "Unknown",
                "text_content": self.resume.text_content if self.resume else ""
            },
            "jd_text": self.jd_text,
            "overall_score": self.overall_score,
            "breakdown": self.get_breakdown(),
            "matched_skills": self.get_matched_skills(),
            "missing_skills": self.get_missing_skills(),
            "suggestions": self.get_suggestions(),
            "interview_questions": self.get_interview_questions(),
            "created_at": self.created_at.isoformat()
        }
