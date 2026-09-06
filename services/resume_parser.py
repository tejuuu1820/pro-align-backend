import os
import re
import json
import pdfplumber
import docx2txt
import requests

def extract_text_from_pdf_pdfplumber(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                val = page.extract_text()
                if val:
                    text += val + "\n"
    except Exception as e:
        print(f"pdfplumber error: {e}")
    return text

def extract_text_from_pdf(file_path):
    return extract_text_from_pdf_pdfplumber(file_path)

def extract_text_from_docx(file_path):
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        print(f"docx2txt error: {e}")
        return ""

def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"txt read error: {e}")
        return ""

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def parse_resume_locally(text):
    email_re = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    phone_re = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
    
    email_match = email_re.search(text)
    phone_match = phone_re.search(text)
    
    email = email_match.group(0) if email_match else ""
    phone = phone_match.group(0) if phone_match else ""
    
    name = ""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if lines:
        for l in lines[:3]:
            if len(l.split()) >= 2 and len(l) < 50 and not email_re.search(l) and not phone_re.search(l):
                name = l
                break
    
    sections = {
        "summary": "",
        "skills": [],
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "languages": []
    }
    
    headers = {
        "summary": ["summary", "professional summary", "about me", "profile"],
        "skills": ["skills", "technical skills", "core competencies", "technologies"],
        "education": ["education", "academic background", "qualification", "studies"],
        "experience": ["experience", "work experience", "employment history", "professional experience"],
        "projects": ["projects", "personal projects", "academic projects", "key projects"],
        "certifications": ["certifications", "certs", "licenses", "courses"],
        "languages": ["languages", "spoken languages"]
    }
    
    current_section = None
    section_buffer = []
    
    for line in lines:
        lower_line = line.lower().strip(":- ")
        matched_section = None
        for sec, keywords in headers.items():
            if lower_line in keywords or any(re.match(rf"^\b{kw}\b", lower_line) for kw in keywords):
                matched_section = sec
                break
        
        if matched_section:
            if current_section:
                sections[current_section] = "\n".join(section_buffer)
            current_section = matched_section
            section_buffer = []
        else:
            if current_section:
                section_buffer.append(line)
                
    if current_section and section_buffer:
        sections[current_section] = "\n".join(section_buffer)
        
    def clean_to_list(sec_text):
        if not sec_text:
            return []
        items = []
        for p in re.split(r'[,;\n•|]', sec_text):
            val = p.strip()
            if val and len(val) < 100:
                items.append(val)
        return items
        
    skills_list = clean_to_list(sections["skills"])
    common_skills = [
        "python", "javascript", "java", "c++", "c#", "ruby", "php", "typescript", "html", "css",
        "react", "angular", "vue", "next.js", "node.js", "express", "flask", "django", "spring",
        "sql", "mysql", "postgresql", "mongodb", "sqlite", "redis", "oracle",
        "docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "ci/cd", "jenkins",
        "agile", "scrum", "project management", "machine learning", "data science", "nlp"
    ]
    if not skills_list:
        for cs in common_skills:
            if re.search(r'\b' + re.escape(cs) + r'\b', text.lower()):
                skills_list.append(cs.title())

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "summary": sections["summary"].strip() or "No summary parsed",
        "skills": list(set(skills_list)),
        "education": clean_to_list(sections["education"]),
        "experience": clean_to_list(sections["experience"]),
        "projects": clean_to_list(sections["projects"]),
        "certifications": clean_to_list(sections["certifications"]),
        "languages": clean_to_list(sections["languages"])
    }

def parse_resume_with_gemini(text, api_key):
    # Stable v1 API endpoint
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) parser. Parse the following resume text and extract structured information.
    Format your response EXACTLY as a single JSON object. Do not include any markdown backticks, explanations, or code formatting.
    
    Fields to extract:
    - name (String)
    - email (String)
    - phone (String)
    - summary (String)
    - skills (Array of Strings)
    - education (Array of Strings)
    - experience (Array of Strings)
    - projects (Array of Strings)
    - certifications (Array of Strings)
    - languages (Array of Strings)

    Resume Text:
    {text}
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
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        if response.status_code == 200:
            res_data = response.json()
            content_text = res_data['candidates'][0]['content']['parts'][0]['text']
            return json.loads(content_text.strip())
        else:
            print(f"Gemini API parse error: {response.text}")
    except Exception as e:
        print(f"Gemini API exception: {e}")
    return None

def parse_resume(file_path, api_key=None):
    raw_text = extract_text(file_path)
    if not raw_text.strip():
        raise ValueError("Could not extract any text from the resume file.")
    
    parsed_info = None
    if api_key:
        parsed_info = parse_resume_with_gemini(raw_text, api_key)
        
    if not parsed_info:
        parsed_info = parse_resume_locally(raw_text)
        
    return raw_text, parsed_info
