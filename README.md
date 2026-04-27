# ⚖️ LegalAssistant - Moroccan Labor Law AI

**LegalAssistant** is a professional-grade, Full-Stack RAG (Retrieval-Augmented Generation) application designed to navigate the complexity of the **Moroccan Labor Code**. It provides accurate, cited, and summarized legal advice through a premium, AI-driven interface.

---

## ✨ Features

- **Semantic Search Engine**: Intelligent retrieval of Moroccan Labor Law articles based on intent, not just keywords.
- **Premium UI/UX**: A state-of-the-art dark-themed React interface featuring glassmorphism, 3D animations, and a responsive lawyer avatar.
- **Extreme Precision**: Advanced regex-based preprocessing of the legal corpus (588 articles) to eliminate noise and maximize retrieval accuracy.
- **Direct Citations**: Every answer is backed by strict references to the relevant Articles of the Moroccan Labor Code.
- **Optimized for French/Arabic Context**: Utilizes multilingual embedding models to maintain high semantic precision in the local legal language.

---

## 🛠️ Technology Stack

### Frontend (User Interface)
- **Vite & React 18**: Used for near-instant hot module replacement and a smooth, component-based single-page application experience.
- **Lucide-React**: Premium iconography for a modern, professional legal aesthetic.
- **Custom CSS Engine**: Implements a dedicated design system with CSS variables, smooth transitions, and high-quality dark-mode aesthetics.

### Backend (The Intelligence)
- **FastAPI**: A high-performance Python framework for handling chat logic and vector database interactions with low latency.
- **ChromaDB**: An AI-native vector database used to store and query legal embeddings with sub-second performance.
- **Sentence-Transformers**: Uses `paraphrase-multilingual-MiniLM-L12-v2` to provide 384-dimensional semantic embeddings, specifically chosen for its high performance in French legal contexts.
- **Groq Cloud (LLM)**: Integrates **Llama-3.3-70B-Versatile** for professional, logical, and concise legal synthesis.

---

## 🏗️ Project Architecture

```text
Law_IA/
├── backend/
│   ├── api/             # FastAPI Application (Logic, Prompting, Retrieval)
│   ├── ingestion/       # Vector DB pipeline (Sanitization, Embedding)
│   ├── data/            # Raw & Structured legal datasets
│   └── chroma_db/       # Persistent Vector Database
├── frontend/
│   └── src/             # Premium React UI Components & Style
└── .env                 # Sensitive API Configurations
```

---

## 🚀 Quick Start

### 1. Prerequisite: API Configuration
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux

# Install requirements
pip install -r requirements.txt

# Run the API
uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The application will be live at `http://localhost:5173`.

---

## 📖 How It Works (RAG Pipeline)
1. **Extraction**: Raw legal text is sanitized via `backend/ingestion/split_articles_fr.py` using advanced Regex to isolate 588 distinct articles.
2. **Embedding**: The text is converted into vector representations using `SentenceTransformer` and stored in **ChromaDB**.
3. **Querying**: User queries are transformed into vectors and matched against the legal database via cosine similarity.
4. **Synthesis**: The top relevant articles are passed into the **Llama-3.3** model with a strict system prompt to generate a structured, emoji-free, professional legal response.

---

> [!IMPORTANT]
> This tool is an assistant and does not replace the advice of a certified legal professional. All legal references should be verified against the official **Bulletin Officiel du Royaume du Maroc**.
