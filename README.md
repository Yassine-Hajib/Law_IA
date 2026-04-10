# ⚖️ Assistant Juridique - Droit du Travail Marocain

Bienvenue sur le projet **Assistant Juridique**, une application web propulsée par l'Intelligence Artificielle qui permet d'interroger le Code du Travail marocain et d'obtenir des réponses sourcées.

Ce projet utilise :

- **Streamlit** pour l'interface utilisateur.
- **Llama 3.1** (via Ollama) pour générer les réponses.
- **ChromaDB** pour la recherche vectorielle des articles de loi.
- **Sentence-Transformers** & **Cross-Encoder** pour la recherche hybride (Retrieval & Reranking).

---

## 🚀 Installation & Prérequis

Pour exécuter le projet sur votre machine, veuillez suivre les étapes suivantes.

### 1. Cloner le projet

Ouvrez un terminal et exécutez la commande suivante :

```bash
git clone https://github.com/Yassine-Hajib/Law_IA.git
cd Law_IA
```

### 2. Installer et configurer l'IA (Llama 3.1 via Ollama)

Le projet utilise le modèle `llama3.1` en local pour fonctionner.

1. Téléchargez et installez **Ollama** depuis le site officiel : [https://ollama.com](https://ollama.com)
2. Une fois installé, ouvrez un terminal et téléchargez le modèle Llama 3.1 :

   ```bash
   ollama pull llama3.1
   ```

3. Assurez-vous qu'Ollama s'exécute en arrière-plan pendant l'utilisation de l'application.

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
   pip install streamlit chromadb requests sentence-transformers
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
3. Le modèle Llama 3.1 analyse ces articles et rédige une réponse précise.
4. Les sources utilisées pour générer la réponse sont affichées à la fin.

---

> **Note :** La base de données vectorielle ChromaDB est située dans le dossier `embeeding/chroma_db`. Assurez-vous que ce dossier est présent pour que la recherche fonctionne correctement.
