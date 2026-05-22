from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
import json
import numpy as np
import re
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=False), override=True)

# Try to import sentence_transformers for local fallback when offline
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

local_model = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load precomputed embeddings into memory
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "..", "data", "json", "precomputed_embeddings.json")

print("Loading vector database...")
embeddings_db = []
try:
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            embeddings_db = json.load(f)
            # Convert embeddings to numpy arrays for faster computation
            for item in embeddings_db:
                item["embedding"] = np.array(item["embedding"])
        print(f"Loaded {len(embeddings_db)} articles.")
    else:
        print(f"Warning: Database file not found at {db_path}")
except Exception as e:
    print(f"Error loading database: {e}")

def get_huggingface_embedding(text: str):
    # Check if local embedding mode is explicitly requested
    use_local = os.getenv("USE_LOCAL_EMBEDDINGS", "false").lower() == "true"
    
    if use_local and HAS_SENTENCE_TRANSFORMERS:
        global local_model
        if local_model is None:
            print("Loading local SentenceTransformer model...")
            local_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        print("Using local SentenceTransformer model to compute embedding.")
        return np.array(local_model.encode(text))

    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        if HAS_SENTENCE_TRANSFORMERS:
            print("HF_TOKEN not found. Falling back to local SentenceTransformer model.")
            if local_model is None:
                local_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            return np.array(local_model.encode(text))
        raise Exception("HF_TOKEN not found in environment variables. Please get a free token from huggingface.co or install sentence-transformers to run locally.")
    
    # Using the free inference API for sentence-transformers
    api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    try:
        response = requests.post(api_url, headers=headers, json={"inputs": [text]}, timeout=10)
        if response.status_code == 200:
            return np.array(response.json()[0])
        else:
            raise Exception(f"Hugging Face API Error: {response.text}")
    except Exception as e:
        # If API call fails (like NameResolutionError), fall back to local model if available
        if HAS_SENTENCE_TRANSFORMERS:
            print(f"Hugging Face API failed ({e}). Falling back to local SentenceTransformer model.")
            if local_model is None:
                local_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            return np.array(local_model.encode(text))
        raise e

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def extract_article_number(text):
    match = re.search(r"article\s*(\d+)", text.lower())
    return match.group(1) if match else "unknown"


def strip_llm_meta_noise(text: str) -> str:
    """Supprime les méta-commentaires (Note:, incomplete, etc.) que le modèle ne doit pas exposer."""
    if not text:
        return text
    # Notes multi-lignes du type (Note: ...)
    text = re.sub(r"\(\s*Note\s*:.*?\)", "", text, flags=re.DOTALL | re.IGNORECASE)
    # Parenthèses anglaises / arabes de type (Note: ...)
    text = re.sub(
        r"\([^)]*(?:\bNote\b|TODO|FIXME|م(?:لاحظة)?\s*(?:للمطور|تقنية)|incomplete|nonsensical|rewrite)[^)]*\)",
        "",
        text,
        flags=re.IGNORECASE,
    )
    lines_out = []
    for line in text.split("\n"):
        lno = line.strip()
        if not lno:
            lines_out.append(line)
            continue
        if re.search(r"^\(?\s*Note\s*:", lno, re.IGNORECASE):
            continue
        if re.search(
            r"\b(incomplete|nonsensical|rewrite properly|still incomplete|need to rewrite)\b",
            lno,
            re.IGNORECASE,
        ):
            continue
        lines_out.append(line)
    return "\n".join(lines_out)


def dedupe_blank_paragraphs(block: str) -> str:
    parts = [p.strip() for p in re.split(r"\n\s*\n+", block) if p.strip()]
    seen = set()
    unique = []
    for p in parts:
        key = re.sub(r"\s+", " ", p)
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return "\n\n".join(unique)


def normalize_arabic_three_section_response(raw: str) -> str:
    """
    Garde une seule fois **الإجابة / التوضيح / الأساس القانوني** (première occurrence de chaque bloc).
    """
    raw = strip_llm_meta_noise(raw)
    # Extraire la première occurrence de chaque section (le modèle répète parfois tout le bloc)
    pat_answer = re.compile(
        r"\*\*الإجابة\s*:\*\*\s*(.*?)(?=\*\*التوضيح\s*:\*\*)",
        re.DOTALL | re.IGNORECASE,
    )
    pat_explain = re.compile(
        r"\*\*التوضيح\s*:\*\*\s*(.*?)(?=\*\*الأساس القانوني\s*:\*\*)",
        re.DOTALL | re.IGNORECASE,
    )
    pat_legal = re.compile(
        r"\*\*الأساس القانوني\s*:\*\*\s*(.*?)(?=\*\*الإجابة\s*:\*\*|\Z)",
        re.DOTALL | re.IGNORECASE,
    )
    ma = pat_answer.search(raw)
    me = pat_explain.search(raw)
    ml = pat_legal.search(raw)
    if ma and me and ml:
        a = dedupe_blank_paragraphs(ma.group(1).strip())
        e = dedupe_blank_paragraphs(me.group(1).strip())
        lg = dedupe_blank_paragraphs(ml.group(1).strip())
        a = strip_llm_meta_noise(a)
        e = strip_llm_meta_noise(e)
        lg = strip_llm_meta_noise(lg)
        return (
            f"**الإجابة :**\n{a}\n\n"
            f"**التوضيح :**\n{e}\n\n"
            f"**الأساس القانوني :**\n{lg}"
        )
    return strip_llm_meta_noise(dedupe_blank_paragraphs(raw.strip()))


class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
def chat(payload: ChatRequest):
    query = payload.query
    query_stripped = query.strip()
    query_processed = query_stripped.lower()

    latin_letters = len(re.findall(r"[a-zA-ZÀ-ÿ]", query_processed))
    arabic_letters = len(re.findall(r"[\u0600-\u06FF]", query_stripped))
    if not query_processed or (latin_letters < 3 and arabic_letters < 3):
        return {
            "response": "**الإجابة :** لم يتم اعتبار السؤال مقبولا.\n\n**التوضيح :** نص الطلب قصير جدا أو فارغ؛ يرجى صياغة استفسار أوضح (ثلاثة أحرف أو أكثر).\n\n**الأساس القانوني :** لا ينطبق.",
            "sources": [],
        }

    if len(query_processed.split()) < 5:
        query_processed = f"droit du travail marocain responsabilités conditions légales article : {query_processed}"

    try:
        # Get embedding from HF API instead of local model
        query_embedding = get_huggingface_embedding(query_processed)

        if not embeddings_db:
             return {"response": "Erreur : La base de données d'articles n'est pas chargée. Assurez-vous d'avoir exécuté precompute_embeddings.py.", "sources": []}

        # Compute similarities using numpy
        similarities = []
        for item in embeddings_db:
            sim = cosine_similarity(query_embedding, item["embedding"])
            similarities.append((sim, item))
        
        # Sort by similarity descending
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # Get top 5 results
        top_results = similarities[:5]
        
        context_parts = []
        top_docs = []
        for sim, item in top_results:
            doc_id = item["id"]
            doc_text = item["text"]
            context_parts.append(f"{doc_id} :\n{doc_text}")
            top_docs.append(f"{doc_id} :\n{doc_text}")

        context = "\n\n".join(context_parts)

    except Exception as e:
        return {
            "response": f"**الإجابة :** تعذر تنفيذ البحث في القاعدة.\n\n**التوضيح :** خطأ تقني أثناء الاسترجاع المعجمي التراكيبي للوثائق: {e}\n\n**الأساس القانوني :** لا ينطبق.",
            "sources": [],
        }

    system_prompt = """Tu es un expert du droit du travail marocain.

LANGUE : arabe moderne standard uniquement (fusḥā), quel que soit le dialecte ou la langue de la question.

FORMAT UNIQUE — À RESPECTER STRICTEMENT :
Tu dois produire EXACTEMENT trois blocs, CHACUN UNE SEULE FOIS, sans les répéter et sans brouillon ni version alternative :

**الإجابة :**
(un paragraphe ou deux, réponse directe au citoyen)

**التوضيح :**
(un paragraphe ou deux, synthèse juridique claire)

**الأساس القانوني :**
(numéros d'articles précis tirés du contexte fourni ; si insuffisant, indiquer en une phrase que le contexte ne permet pas de citer sans inventer)

INTERDICTIONS ABSOLUES (ne jamais écrire pour l'utilisateur final) :
- Aucune phrase en anglais sauf numéro d'article si déjà ainsi dans la source.
- Aucune méta-note : pas de « Note: », « incomplete », « rewrite », « nonsensical », « TODO », pas de commentaire entre parenthèses sur la qualité du texte.
- Pas de répétition du même bloc juridique plusieurs fois.
- Pas de lignes horizontales décoratives (---), pas de plusieurs en-têtes **الإجابة** dans une même réponse.
- Pas d'émojis ni de formules de salutation.

STYLE : ton administratif sobre ; tu parles au citoyen, pas au développeur.
Si une notion familière correspond à un terme juridique officiel (ex. « الخدمة » pour le travail salarié), réponds avec le vocabulaire du Code du travail marocain sans moraliser.
"""

    user_prompt = f"المرجعيات القانونية المقتطفة :\n{context}\n\nسؤال المستخدم :\n{query}\n"

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    if not GROQ_API_KEY:
        return {
            "response": "**الإجابة :** الخدمة غير مهيأة.\n\n**التوضيح :** مفتاح برمجية واجهة Groq غير موجود في الإعداد (.env).\n\n**الأساس القانوني :** لا ينطبق.",
            "sources": [],
        }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0
            },
            timeout=60
        )

        if response.status_code != 200:
            return {
                "response": f"**الإجابة :** فشل الاتصال بمنصة توليف النصوص.\n\n**التوضيح :** خطأ خارجي برمز الحالة ({response.status_code}).\n\n**الأساس القانوني :** لا ينطبق.",
                "sources": [],
            }

        data = response.json()
        full_response = data["choices"][0]["message"]["content"]
        full_response = normalize_arabic_three_section_response(full_response)

        return {
            "response": full_response,
            "sources": top_docs
        }

    except Exception as e:
        return {
            "response": f"**الإجابة :** خطأ أثناء توليد المسودة الذكية.\n\n**التوضيح :** {e}\n\n**الأساس القانوني :** لا ينطبق.",
            "sources": [],
        }
