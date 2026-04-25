# ⚖️ Assistant Juridique - Droit du Travail Marocain

Bienvenue sur le projet **Assistant Juridique**, une application web propulsée par l'Intelligence Artificielle qui permet d'interroger le Code du Travail marocain et d'obtenir des réponses sourcées.

Ce projet utilise :

- **Streamlit** pour l'interface utilisateur.
- **Groq API / OpenAI** (modèle `openai/gpt-oss-120b` par défaut) pour générer les réponses.
- **ChromaDB** pour la recherche vectorielle et le stockage des articles de loi.
- **Sentence-Transformers** (`BAAI/bge-small-en`) pour générer les embeddings des requêtes.
- **Cross-Encoder** (`cross-encoder/ms-marco-MiniLM-L-6-v2`) pour le reranking des résultats de recherche pertinents.

---

## 🚀 Installation & Prérequis

Pour exécuter le projet sur votre machine, veuillez suivre les étapes suivantes.

### 1. Cloner le projet

Ouvrez un terminal et exécutez la commande suivante :

```bash
git clone https://github.com/Yassine-Hajib/Law_IA.git
cd Law_IA
```

### 2. Configurer l'IA (Groq API)

Le projet utilise l'API Groq (compatible OpenAI) avec le modèle `openai/gpt-oss-120b` par défaut.

1. Créez une clé API sur le site Groq : [https://console.groq.com](https://console.groq.com)
2. Configurez vos variables d'environnement (méthode recommandée avec `.env`) :

   ```bash
   cp .env.example .env
   # puis éditez .env et ajoutez votre vraie clé
   ```

3. (Optionnel) Choisissez un autre modèle Groq dans `.env` :

   ```bash
   GROQ_MODEL="llama-3.1-70b-versatile"
   ```

### 3. Installer les dépendances Python

Il est fortement recommandé d'utiliser un environnement virtuel.

1. **Créer et activer un environnement virtuel :**

   ```bash
   python -m venv env
   
   # Sur Windows :
   env\Scripts\activate
   
   # Sur Mac/Linux :
   source env/bin/activate
   ```

2. **Installer les librairies requises :**
   Installez les dépendances principales avec la commande suivante :

   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Démarrer l'application

Une fois l'installation terminée, vous pouvez lancer l'interface web.

Dans le dossier du projet, tapez la commande suivante :

```bash
streamlit run Scripts/retrieval/app.py
```

L'application s'ouvrira automatiquement dans votre navigateur par défaut (généralement à l'adresse `http://localhost:8501`).

---

## 📜 Fonctionnement

1. Entrez votre question concernant le droit du travail marocain.
2. L'application recherche les articles de loi pertinents dans la base de données.
3. Le modèle via Groq API (`openai/gpt-oss-120b` par défaut) analyse ces articles et rédige une réponse précise.
4. Les sources utilisées pour générer la réponse sont affichées à la fin.

---

> **Note :** La base de données vectorielle ChromaDB est située dans le dossier `embeeding/chroma_db`. Assurez-vous que ce dossier est présent pour que la recherche fonctionne correctement.
