import re
import json
import os
from backend.services.matcher import analyze_keywords

CATEGORIES = {
    "Programming Languages": ["python", "javascript", "java", "c++", "c#", "ruby", "php", "typescript", "golang", "rust", "scala", "kotlin", "swift", "sql", "html", "css"],
    "Frameworks": ["react", "angular", "vue", "next.js", "node.js", "express", "flask", "django", "fastapi", "spring", "spring boot", "laravel", "asp.net"],
    "Libraries": ["pandas", "numpy", "scikit-learn", "scikit learn", "matplotlib", "tensorflow", "pytorch", "keras", "spacy", "nltk", "opencv"],
    "AI/ML": ["machine learning", "data science", "nlp", "xgboost", "deep learning", "artificial intelligence"],
    "Version Control": ["git", "github", "gitlab"],
    "Cloud": ["aws", "azure", "gcp", "google cloud", "cloud computing"],
    "DevOps": ["docker", "kubernetes", "k8s", "ci/cd", "ci-cd", "jenkins", "terraform", "ansible"]
}

def load_resources():
    try:
        path = os.path.join(os.path.dirname(__file__), 'learning_resources.json')
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def categorize_skills(skills_list):
    categorized = {cat: [] for cat in CATEGORIES.keys()}
    categorized["Other Tools"] = []
    
    for skill in skills_list:
        skill_lower = skill.lower().strip()
        found = False
        for category, keywords in CATEGORIES.items():
            if any(kw in skill_lower or skill_lower in kw for kw in keywords):
                categorized[category].append(skill)
                found = True
                break
        if not found:
            categorized["Other Tools"].append(skill)
            
    # Remove empty categories
    return {k: v for k, v in categorized.items() if len(v) > 0}

def extract_experience_years(text):
    text_lower = text.lower()
    patterns = [
        r'(\d+)\+?\s*(?:years|yrs)\b',
        r'(\d+)\s*(?:years|yrs)\s+of\s+experience',
    ]
    max_years = 0
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            try:
                years = int(match)
                if years > max_years and years < 45:
                    max_years = years
            except ValueError:
                pass
    if max_years == 0:
        years_range = re.findall(r'\b(20\d{2})\b\s*[-–—]\s*\b(20\d{2}|present|current)\b', text_lower)
        total_yrs = 0
        for start, end in years_range:
            try:
                s_yr = int(start)
                e_yr = 2026 if (end == 'present' or end == 'current') else int(end)
                diff = e_yr - s_yr
                if 0 < diff < 15:
                    total_yrs += diff
            except ValueError:
                pass
        max_years = max(max_years, total_yrs)
    return max_years if max_years > 0 else 2

def extract_education_level(text):
    text_lower = text.lower()
    if any(term in text_lower for term in ["phd", "ph.d", "doctorate"]):
        return 3
    if any(term in text_lower for term in ["master", "m.s", "msc", "mba", "m.tech"]):
        return 2
    return 1 # Bachelor

def calculate_ats_card(resume_metadata, resume_text, jd_keywords, jd_text, semantic_score):
    """
    Computes structural scores and categorizations.
    """
    # Keyword Matching on Entire Resume Text
    matched, missing = analyze_keywords(resume_text, jd_keywords)
    
    # 1. Skills score (40% weight)
    total_keywords = len(jd_keywords)
    skills_score = min(len(matched) / total_keywords * 100, 100.0) if total_keywords > 0 else 100.0
    
    # 2. Experience score (20% weight)
    jd_exp = extract_experience_years(jd_text)
    res_exp = extract_experience_years(resume_text)
    exp_score = 100.0 if res_exp >= jd_exp else (res_exp / jd_exp) * 100.0 if jd_exp > 0 else 100.0
    
    # 3. Projects score (15% weight)
    projects_content = " ".join(resume_metadata.get("projects", []))
    if projects_content and total_keywords > 0:
        proj_matched = [kw for kw in jd_keywords if kw.lower() in projects_content.lower()]
        proj_score = min(len(proj_matched) / (total_keywords * 0.4) * 100, 100.0)
    else:
        proj_score = skills_score
        
    # 4. Education score (10% weight)
    jd_edu = extract_education_level(jd_text)
    res_edu = extract_education_level(resume_text)
    edu_score = 100.0 if res_edu >= jd_edu else 70.0
    
    # 5. Semantic similarity score (10% weight)
    sem_score = float(semantic_score)
    
    # 6. Formatting score (5% weight)
    formatting_score = 100
    if len(resume_text) < 400:
        formatting_score -= 30
    if len(resume_text) > 9000:
        formatting_score -= 10
    if "  " in resume_text:
        formatting_score -= 5
    formatting_score = max(formatting_score, 50)
    
    # Calculate overall score
    overall = round(
        (skills_score * 0.40) +
        (exp_score * 0.20) +
        (proj_score * 0.15) +
        (edu_score * 0.10) +
        (sem_score * 0.10) +
        (formatting_score * 0.05)
    )
    
    # Form explanation additions / deductions
    explanations = [
        {"label": "Skills Matching", "value": round(skills_score * 0.40), "sign": "+"},
        {"label": "Experience Alignment", "value": round(exp_score * 0.20), "sign": "+"},
        {"label": "Projects Matching", "value": round(proj_score * 0.15), "sign": "+"},
        {"label": "Education Level", "value": round(edu_score * 0.10), "sign": "+"},
        {"label": "Semantic Boost", "value": round(sem_score * 0.10), "sign": "+"},
        {"label": "Formatting Accuracy", "value": round(formatting_score * 0.05), "sign": "+"}
    ]
    # Penalize for missing high-priority keywords
    for item in missing[:2]:
        explanations.append({"label": f"Missing {item}", "value": -3, "sign": "-"})
        
    # Categorize matched/missing
    matched_categorized = categorize_skills(matched)
    missing_categorized = categorize_skills(missing)
    
    # Map missing learning resources
    resources = load_resources()
    missing_resources = []
    for item in missing:
        item_title = item.title()
        res_info = resources.get(item_title, {
            "difficulty": "Medium",
            "time": "1 week",
            "youtube": "https://www.youtube.com/results?search_query=learn+" + item.replace(" ", "+"),
            "docs": "https://www.google.com/search?q=" + item.replace(" ", "+") + "+documentation"
        })
        missing_resources.append({
            "skill": item,
            "difficulty": res_info["difficulty"],
            "time": res_info["time"],
            "youtube": res_info["youtube"],
            "docs": res_info["docs"]
        })
        
    # Probability metrics
    pass_prob = "High" if overall >= 80 else ("Medium" if overall >= 60 else "Low")
    readability = "Excellent" if formatting_score >= 90 else ("Good" if formatting_score >= 70 else "Fair")
    keyword_coverage = round(len(matched) / max(total_keywords, 1) * 100)
    
    # Strengths / Gaps Highlights
    strengths = []
    if skills_score >= 70:
        strengths.append("Strong Technical Skill Overlap")
    if res_exp >= jd_exp:
        strengths.append("Meets Experience Requirements")
    if len(resume_metadata.get("projects", [])) >= 2:
        strengths.append("Rich Hands-on Project History")
    if not strengths:
        strengths.append("Standard Section Formatting")
        
    # Recruiter feedback fallback
    feedback_summary = (
        f"The candidate exhibits an overall match of {overall}%. "
        f"Strengths include extensive projects matching {proj_score:.0f}% requirements. "
        f"However, key developer tools like {', '.join(missing[:2])} are absent from the resume corpus. "
        f"Recommend candidate for screening interview following resume updates."
    )
    
    return {
        "scores": {
            "overall": overall,
            "skills": round(skills_score),
            "projects": round(proj_score),
            "experience": round(exp_score),
            "education": round(edu_score),
            "semantic": round(sem_score),
            "formatting": round(formatting_score)
        },
        "matched_skills": matched,
        "missing_skills": missing,
        "matched_categorized": matched_categorized,
        "missing_categorized": missing_categorized,
        "missing_resources": missing_resources,
        "explanations": explanations,
        "pass_probability": pass_prob,
        "readability": readability,
        "keyword_coverage": keyword_coverage,
        "strengths": strengths,
        "recruiter_feedback": feedback_summary
    }
