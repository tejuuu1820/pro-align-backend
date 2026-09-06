import os
import re
from backend.services.resume_parser import extract_text

def clean_jd_text(text):
    return text.strip()

# List of typical high-value tech keywords to look for
TECH_KEYWORDS = [
    # Languages
    "python", "javascript", "java", "c++", "c#", "ruby", "php", "typescript", "golang", "rust", "scala", "kotlin", "swift",
    "html", "css", "sql", "pl/sql", "no-sql", "nosql",
    # Frameworks/Libraries
    "react", "angular", "vue", "next.js", "nuxt", "node.js", "node", "express", "flask", "django", "fastapi", "spring boot", "spring",
    "laravel", "asp.net", "dotnet", "jquery", "bootstrap", "tailwind", "framer motion",
    # Data & ML
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "spacy", "nltk", "opencv", "spark", "hadoop",
    "powerbi", "tableau", "excel",
    # Clouds & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "jenkins", "gitlab", "github", "ci/cd", "terraform",
    "ansible", "prometheus", "grafana", "linux", "bash",
    # Databases
    "mysql", "postgresql", "postgres", "mongodb", "sqlite", "redis", "oracle", "mariadb", "cassandra", "dynamodb",
    # Concepts & Methodologies
    "agile", "scrum", "kanban", "devops", "sdlc", "rest api", "graphql", "microservices", "oop", "system design", "git",
    "unit testing", "jest", "pytest", "cypress", "security", "ci-cd", "cloud computing"
]

def extract_keywords_from_jd(text):
    text_lower = text.lower()
    found_keywords = set()
    
    # Simple word match
    for kw in TECH_KEYWORDS:
        # Match using word boundaries to avoid false positives (e.g. "go" matching in "good")
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, text_lower):
            found_keywords.add(kw.title())
            
    # Also look for multi-word phrases or special cases
    special_cases = {
        "project management": "Project Management",
        "product management": "Product Management",
        "data science": "Data Science",
        "machine learning": "Machine Learning",
        "artificial intelligence": "Artificial Intelligence",
        "deep learning": "Deep Learning",
        "natural language processing": "Natural Language Processing",
        "soft skills": "Soft Skills",
        "team lead": "Team Lead",
        "agile pm": "Agile PM",
        "ui/ux": "UI/UX",
        "ui ux": "UI/UX"
    }
    
    for phrase, clean_val in special_cases.items():
        if phrase in text_lower:
            found_keywords.add(clean_val)
            
    return list(found_keywords)
