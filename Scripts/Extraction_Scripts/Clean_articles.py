import json
import re


with open("Data/articles_raw.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

cleaned_articles = {}

for article_num, text in articles.items():
  
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)  # Remove multiple spaces

    
    text = re.sub(r"\b\d+\b", lambda m: m.group()  # Remove page numbers 
                  if int(m.group()) < 2000 else "", text)
    
    text = text.strip() # Trim spaces

    cleaned_articles[article_num] = text

# Savee It
with open("Data/articles_clean.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_articles, f, ensure_ascii=False, indent=2)

print(f"{len(cleaned_articles)} articles cleaned and saved.")
