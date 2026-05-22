# ⚖️ LegalAssistant — Moroccan Labor Law AI

A professional AI tool that answers questions about the **Moroccan Labor Code**, with citations to the exact legal articles.

---

## 🚀 How to Start the App (Easy Way)

### Step 1 — First Time Only: Add your API Keys

1. In the `Law_IA` folder, find the file named **`.env`**
2. Open it with Notepad
3. Make sure it contains your API keys (replace `your_key_here` with your real keys):
   ```env
   GROQ_API_KEY=your_groq_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   HF_TOKEN=your_huggingface_token_here
   ```
   * 🔑 **Groq API Key**: Sign up and get a free key at [console.groq.com](https://console.groq.com/keys).
   * 🔑 **Hugging Face Token**: Sign up and get a free Read access token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens). This is required to generate query embeddings using the Hugging Face Serverless Inference API.

### Step 2 — Launch the App

Double-click the launcher script in the root directory:

> ### 👉 `start.bat`

A few windows will open. **Wait about 15 seconds**, and your default browser will open automatically pointing to the app at:
* **Frontend UI**: [http://localhost:5173](http://localhost:5173)
* **Backend API**: [http://localhost:8000](http://localhost:8000)

### Step 3 — Use the App

* Type your legal question in the chat box (in French or Arabic).
* The AI will analyze the query, retrieve relevant law articles, and answer in professional modern standard Arabic (Fusḥā) with the exact article numbers from the Moroccan Labor Code.

### Step 4 — Stop the App

When you're done, double-click the stop script in the root directory to release the network ports:

> ### 👉 `stop.bat`

---

## ⚙️ Requirements

Make sure you have these installed on your computer (one-time setup):

| Tool | Download Link | Purpose |
|------|--------------|---------|
| Python 3.10+ | https://www.python.org/downloads/ | Runs the FastAPI Backend API |
| Node.js 18+ | https://nodejs.org/ | Runs the React (Vite) Frontend |

---

## 📁 Project Structure

```text
Law_IA/
├── start.bat          ← Double-click to START the app
├── stop.bat           ← Double-click to STOP the app
├── .env               ← Your API keys (keep this private!)
├── requirements.txt   ← Python dependencies
├── backend/           ← The AI Search Engine (FastAPI)
│   ├── api/
│   │   └── main.py    ← Backend API server
│   └── data/
│       └── json/
│           └── precomputed_embeddings.json ← Pre-computed law embeddings
└── frontend/          ← The User Interface (React + Vite)
```

---

> ⚠️ **Disclaimer**: This tool is an AI assistant designed for informational and guiding purposes. It does not replace the advice of a certified legal professional. Always verify responses against the official publication in the Moroccan Bulletin Officiel (الجريدة الرسمية).

