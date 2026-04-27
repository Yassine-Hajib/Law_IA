import re
import json

with open("../data/json/full_law.txt", "r", encoding="utf-8") as f:
    text = f.read()

def clean_text(raw_text):
    # Remove large structural noises that bleed into the end of articles
    cleaned = re.sub(r'(Livre|Titre|Chapitre|Section)[\s\w]+:.*?(?=\n|$)', '', raw_text, flags=re.IGNORECASE)
    cleaned = re.sub(r'(Livre|Titre|Chapitre|Section)[\s\w]+(?=\n|$)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Bulletin Officiel.*?(?=\n|$)', '', cleaned, flags=re.IGNORECASE)
    # Clean whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

pattern = r"(Article\s+\d+)"
parts = re.split(pattern, text)

articles = {}
structured = []
for i in range(1, len(parts), 2):
    article_title = parts[i]
    article_text = parts[i + 1]
    
    article_number = article_title.replace("Article", "").strip()
    cleaned_txt = clean_text(article_text)
    
    articles[article_number] = cleaned_txt
    structured.append({"article_id": f"Article {article_number}", "text": cleaned_txt})

with open("../data/json/articles_raw.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

with open("../data/json/structred_Law_Article.json", "w", encoding="utf-8") as f:
    json.dump(structured, f, ensure_ascii=False, indent=2)

print(f"{len(articles)} clean articles generated and saved.")
