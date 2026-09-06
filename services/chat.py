import requests

def get_local_chat_response(query, missing_skills):
    query_lower = query.lower()
    missing_str = ", ".join(missing_skills[:3]) if missing_skills else "Docker, AWS, Kubernetes"
    
    if "docker" in query_lower:
        return "Docker is highly recommended for this role. It helps you package services into container instances to guarantee consistency between staging and production environments."
    elif "aws" in query_lower or "cloud" in query_lower:
        return "Cloud exposure (specifically AWS) is required for deployment and scale. Learn basic services like EC2, S3, and RDS to fill this gap."
    elif "project" in query_lower:
        return f"To improve matching, build a backend web application using Python, Flask, and SQLite, containerize it using Docker, and configure a CI/CD pipeline."
    elif "salary" in query_lower:
        return "Salary expectations depend on location and level. Typically, a backend developer with this skill set commands between $90k and $130k in modern tech hubs."
    elif "improve" in query_lower:
        return f"To improve your match score, integrate these missing keywords into your project bullets: {missing_str}."
    
    return f"As your AI career coach, I suggest focusing on learning {missing_str} and building mock deployment projects to address the job description gaps."

def ask_career_coach(query, resume_text, jd_text, history_list=None, api_key=None):
    if not api_key:
        from backend.services.jd_parser import extract_keywords_from_jd
        from backend.services.matcher import analyze_keywords
        jd_keywords = extract_keywords_from_jd(jd_text)
        _, missing = analyze_keywords(resume_text, jd_keywords)
        return get_local_chat_response(query, missing)
        
    # Stable v1 API endpoint
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    history_prompt = ""
    if history_list and isinstance(history_list, list):
        for h in history_list:
            role = "User" if h.get("sender") == "user" else "Coach"
            history_prompt += f"{role}: {h.get('text')}\n"
            
    system_instruction = f"""
    You are 'PRO-ALIGN AI Career Coach', a helpful, professional, and knowledgeable technical recruiter and career consultant.
    You help the candidate analyze their resume match against a Job Description (JD).
    
    Resume Context:
    {resume_text[:2000]}
    
    JD Context:
    {jd_text[:1200]}
    
    Previous Conversation History:
    {history_prompt}
    
    Candidate's Question:
    "{query}"
    
    Provide a professional, direct, and actionable answer. Keep it concise (under 4 sentences if possible) unless a detailed explanation is requested.
    Do not mention configuration files or API limits. Focus on software engineering advice.
    """
    
    payload = {
        "contents": [{
            "parts": [{
                "text": system_instruction
            }]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=12)
        if response.status_code == 200:
            res_data = response.json()
            return res_data['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"Gemini Coach Chat Error: {e}")
        
    from backend.services.jd_parser import extract_keywords_from_jd
    from backend.services.matcher import analyze_keywords
    jd_keywords = extract_keywords_from_jd(jd_text)
    _, missing = analyze_keywords(resume_text, jd_keywords)
    return get_local_chat_response(query, missing)
