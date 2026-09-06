import math
import re
from backend.services.embedding_service import get_embeddings

def compute_cosine_similarity(vec1, vec2):
    if not vec1 or not vec2:
        return 0.0
    try:
        dot = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))
        if mag1 > 0 and mag2 > 0:
            return dot / (mag1 * mag2)
    except Exception as e:
        print(f"Cosine similarity math error: {e}")
    return 0.0

def compute_cosine_similarity_pure_python(text1, text2):
    """
    Pure Python Term-Frequency Cosine Similarity fallback.
    """
    words1 = re.findall(r'\b\w+\b', text1.lower())
    words2 = re.findall(r'\b\w+\b', text2.lower())
    
    tf1 = {}
    tf2 = {}
    for w in words1:
        tf1[w] = tf1.get(w, 0) + 1
    for w in words2:
        tf2[w] = tf2.get(w, 0) + 1
        
    vocab = set(tf1.keys()).union(set(tf2.keys()))
    
    dot_product = 0.0
    for w in vocab:
        dot_product += tf1.get(w, 0) * tf2.get(w, 0)
        
    mag1 = math.sqrt(sum(val**2 for val in tf1.values()))
    mag2 = math.sqrt(sum(val**2 for val in tf2.values()))
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
        
    return dot_product / (mag1 * mag2)

def compute_semantic_similarity(resume_text, jd_text, api_key=None):
    """
    Calculates semantic similarity using hybrid embeddings or pure-python fallback.
    """
    vec_res = get_embeddings(resume_text, api_key)
    vec_jd = get_embeddings(jd_text, api_key)
    
    if vec_res and vec_jd:
        sim = compute_cosine_similarity(vec_res, vec_jd)
        # Shift scale (embeddings are usually positive, let's normalize to 0-100)
        scaled_sim = (sim - 0.3) / 0.7 * 100
        return min(max(round(scaled_sim, 2), 0.0), 100.0)
        
    # Full fallback
    raw_sim = compute_cosine_similarity_pure_python(resume_text, jd_text)
    scaled_sim = raw_sim * 220 # scale TF overlap percentage
    return min(max(round(scaled_sim, 2), 0.0), 100.0)

def analyze_keywords(resume_text, jd_keywords):
    """
    Scans entire resume text corpus for JD keywords case-insensitively.
    """
    resume_text_lower = resume_text.lower()
    matched = []
    missing = []
    
    for kw in jd_keywords:
        kw_clean = kw.strip()
        kw_lower = kw_clean.lower()
        
        # Word boundary pattern search
        pattern = r'\b' + re.escape(kw_lower) + r'\b'
        if re.search(pattern, resume_text_lower):
            matched.append(kw_clean)
        else:
            # Substring fallback for combined skills (e.g. CI/CD)
            if kw_lower in resume_text_lower:
                matched.append(kw_clean)
            else:
                missing.append(kw_clean)
                
    return list(set(matched)), list(set(missing))
