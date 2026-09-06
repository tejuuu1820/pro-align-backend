import requests

_transformer_model = None
try:
    from sentence_transformers import SentenceTransformer
    _transformer_model = False 
except ImportError:
    pass

def get_offline_model():
    global _transformer_model
    if _transformer_model is False:
        try:
            _transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Offline SentenceTransformer load error: {e}")
            _transformer_model = None
    return _transformer_model

def get_gemini_embedding(text, api_key):
    # Stable v1 API endpoint
    url = f"https://generativelanguage.googleapis.com/v1/models/text-embedding-004:embedContent?key={api_key}"
    payload = {
        "model": "models/text-embedding-004",
        "content": {
            "parts": [{
                "text": text[:3000]
            }]
        }
    }
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8)
        if response.status_code == 200:
            return response.json().get('embedding', {}).get('values', [])
    except Exception as e:
        print(f"Gemini embedding retrieval error: {e}")
    return None

def get_offline_embedding(text):
    model = get_offline_model()
    if model:
        try:
            return model.encode(text).tolist()
        except Exception as e:
            print(f"Offline embedding extraction error: {e}")
    return None

def get_embeddings(text, api_key=None):
    if api_key:
        emb = get_gemini_embedding(text, api_key)
        if emb:
            return emb
            
    return get_offline_embedding(text)
