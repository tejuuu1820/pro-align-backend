import requests
import json
import re

def generate_local_suggestions(matched_skills, missing_skills):
    suggestions = []
    
    if "Flask" in matched_skills or "Rest Api" in matched_skills:
        suggestions.append("✓ Mention Flask REST APIs in your Summary.")
    else:
        suggestions.append("✓ Consider integrating REST API architecture concepts in projects.")
        
    if "Git" not in matched_skills and "Github" not in matched_skills:
        suggestions.append("✓ Mention Git in Skills or Project bullets.")
        
    if "Docker" in missing_skills:
        suggestions.append("✓ Add Docker after learning it to validate containerization capability.")
    if "Aws" in missing_skills:
        suggestions.append("✓ Add AWS certification or mention basic cloud services.")
        
    suggestions.append("✓ Quantify project outcomes (e.g. 'improved performance by 20%').")
    suggestions.append("✓ Mention API deployment pipelines or cloud deployment.")
    
    if "Postgresql" in missing_skills or "Sql" in missing_skills:
        suggestions.append("✓ Add PostgreSQL database design references.")
        
    return suggestions

def generate_suggestions(matched_skills, missing_skills, resume_metadata, api_key=None):
    if not api_key:
        return generate_local_suggestions(matched_skills, missing_skills)
        
    # Stable v1 API endpoint
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
    You are an expert resume writer. Review these matching metrics:
    Matched: {', '.join(matched_skills)}
    Missing: {', '.join(missing_skills)}
    Resume Metadata: {json.dumps(resume_metadata)}
    
    Generate 5-6 highly customized, short improvement bullet points.
    Each bullet MUST start with '✓' and be short, e.g.:
    '✓ Mention Flask REST APIs in your Summary.'
    '✓ Add Docker after learning it.'
    '✓ Quantify project outcomes.'
    
    Format the response as a single, valid JSON array of strings. Do not wrap in markdown block text.
    """
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=12)
        if response.status_code == 200:
            res_data = response.json()
            content_text = res_data['candidates'][0]['content']['parts'][0]['text']
            return json.loads(content_text.strip())
    except Exception as e:
        print(f"Gemini suggestions generation error: {e}")
        
    return generate_local_suggestions(matched_skills, missing_skills)

def rewrite_section_locally(section_name, section_content, missing_skills):
    strong_verbs = {
        "helped": "facilitated",
        "made": "engineered",
        "used": "leveraged",
        "wrote": "architected",
        "worked on": "implemented",
        "responsible for": "spearheaded",
        "managed": "orchestrated",
        "built": "pioneered",
        "improved": "optimized"
    }
    text = section_content
    for weak, strong in strong_verbs.items():
        text = re.sub(rf'\b{weak}\b', strong, text, flags=re.I)
        
    name_lower = section_name.lower()
    if "skills" in name_lower and missing_skills:
        text += ", " + ", ".join([s.title() for s in missing_skills[:3]])
    elif "summary" in name_lower:
        if missing_skills:
            text = f"Result-oriented professional with extensive expertise in backend development, leveraging strong foundations in {', '.join(missing_skills[:2])}. " + text
        else:
            text = "Accomplished software engineer with a track record of building high-performance, modular services. " + text
    elif "experience" in name_lower or "projects" in name_lower:
        lines = text.split('\n')
        new_lines = []
        for line in lines:
            line = line.strip()
            if line:
                if not line.startswith(('•', '-', '*')):
                    line = "• " + line
                if missing_skills and "utilizing" not in line.lower():
                    line += f" utilizing {missing_skills[0]}"
                    missing_skills = missing_skills[1:] + [missing_skills[0]]
                new_lines.append(line)
        text = "\n".join(new_lines)
        
    return text

def rewrite_section(section_name, section_content, missing_skills, jd_text, api_key=None):
    if not api_key:
        return rewrite_section_locally(section_name, section_content, missing_skills)
        
    # Stable v1 API endpoint
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
    You are an expert resume writer. Optimize the following resume section to make it ATS compatible.
    
    Section Name: {section_name}
    Original Content:
    {section_content}
    
    JD Requirements:
    {jd_text[:1200]}
    
    Missing keywords to integrate:
    {', '.join(missing_skills)}
    
    Provide ONLY the rewritten text, formatted as bullets if it's experience/projects. Do not include markdown banners, quotes, or explanations.
    """
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=12)
        if response.status_code == 200:
            res_data = response.json()
            content_text = res_data['candidates'][0]['content']['parts'][0]['text']
            return content_text.strip()
    except Exception as e:
        print(f"Gemini Section Rewrite Error: {e}")
        
    return rewrite_section_locally(section_name, section_content, missing_skills)
