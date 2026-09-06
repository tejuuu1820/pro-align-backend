import requests

def generate_local_cover_letter(resume_metadata, jd_text):
    name = resume_metadata.get("name", "Applicant")
    email = resume_metadata.get("email", "email@example.com")
    phone = resume_metadata.get("phone", "")
    skills = resume_metadata.get("skills", [])
    skills_str = ", ".join(skills[:4]) if skills else "software engineering"
    
    letter = f"""{name}
{email} | {phone}

Dear Hiring Manager,

I am writing to express my strong interest in the software engineering position. With a robust background in software development and hands-on experience leveraging technologies like {skills_str}, I am confident in my ability to immediately add value to your team.

My resume details my experience building scale, designing database schemas, and writing clean backend microservices. I am particularly drawn to your organization's focus on technical excellence and engineering innovations.

Thank you for your time and consideration. I look forward to the opportunity to discuss how my qualifications align with your engineering goals.

Sincerely,
{name}"""
    return letter

def generate_cover_letter(resume_metadata, resume_text, jd_text, api_key=None):
    if not api_key:
        return generate_local_cover_letter(resume_metadata, jd_text)
        
    # Stable v1 API endpoint
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
    You are an expert career consultant. Write a professional, tailored Cover Letter based on the following candidate details and Job Description.
    
    Candidate Name: {resume_metadata.get('name', 'Applicant')}
    Candidate Contact: {resume_metadata.get('email', '')} | {resume_metadata.get('phone', '')}
    Resume Details:
    {resume_text[:2000]}
    
    Job Description:
    {jd_text[:1200]}
    
    The Cover Letter should be engaging, write about overlapping skills, mention achievements, and be copyable. 
    Provide ONLY the cover letter text. Do not include markdown headers, surrounding text, or descriptions.
    """
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        if response.status_code == 200:
            res_data = response.json()
            return res_data['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"Gemini Cover Letter API Error: {e}")
        
    return generate_local_cover_letter(resume_metadata, jd_text)
