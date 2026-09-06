from datetime import datetime
from backend.models.database import db
import json

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    text_content = db.Column(db.Text, nullable=False)
    
    # Store metadata JSON (skills, contact, education, etc.)
    metadata_json = db.Column(db.Text, nullable=False, default="{}")
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reports = db.relationship('AnalysisReport', backref='resume', lazy=True, cascade="all, delete-orphan")

    def get_metadata(self):
        try:
            return json.loads(self.metadata_json)
        except Exception:
            return {}

    def set_metadata(self, data):
        self.metadata_json = json.dumps(data)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "metadata": self.get_metadata(),
            "uploaded_at": self.uploaded_at.isoformat()
        }
