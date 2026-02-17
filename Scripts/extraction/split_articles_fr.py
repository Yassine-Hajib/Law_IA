import re
import json


with open("Data/full_law.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Define the article pattern
pattern = r"(Article\s+\d+)"


# Split the text automatically
parts = re.split(pattern, text)


articles = {}

for i in range(1, len(parts), 2):
    article_title = parts[i]          # "Article 1"
    article_text = parts[i + 1].strip()
    
    article_number = article_title.replace("Article", "").strip()
    articles[article_number] = article_text

# Save result
with open("Data/articles_raw.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"{len(articles)} articles detected and saved.")
