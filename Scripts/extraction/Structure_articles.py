import json

LAW_NAME = "Code du travail marocain"
LANGUAGE = "fr"

# Load cleaned articles
with open("Data/articles_clean.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

structured_articles = []

for article_number, text in articles.items():
    article_object = {
        "article_id": f"Art_{article_number}",
        "article_number": int(article_number),
        "law_name": LAW_NAME,
        "language": LANGUAGE,
        "text": text,
        "source": "official_pdf"
    }

    structured_articles.append(article_object) 

# Save structured file
with open("Data/articles_structured.json", "w", encoding="utf-8") as f:
    json.dump(structured_articles, f, ensure_ascii=False, indent=2)

print(f"{len(structured_articles)} articles structured successfully.")

