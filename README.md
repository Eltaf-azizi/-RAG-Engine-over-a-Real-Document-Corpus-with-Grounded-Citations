<h1 align="center">Constitutional RAG Q&A System</h1>

> Retrieval-Augmented Generation over Real Constitutional Documents with Grounded Citations

Hey! This is my RAG project — it answers questions about constitutions from 6 countries, always cites its sources, and refuses to make stuff up when it doesn't know the answer.

---
## 🤔 What is this?

I built this to solve a simple problem: LLMs hallucinate. They confidently make up facts that sound real but aren't. When you're dealing with constitutional law, that's a problem.

So this system:
1. Takes your question
2. Searches through real constitution PDFs
3. Finds the most relevant sections
4. Tells the LLM: "Answer using ONLY this, and cite everything"
5. If nothing relevant is found → "I don't have enough information"

No more guessing. No more fake citations.

---

## 🌍 Countries Covered

| Country | Document | Chunks |
|---------|----------|--------|
| 🇺🇸 USA | Constitution | 647 |
| 🇫🇷 France | Constitution of 1958 | 202 |
| 🇩🇪 Germany | Basic Law | 470 |
| 🇵🇰 Pakistan | Constitution of 1973 | 975 |
| 🇳🇴 Norway | Constitution of 1814 | 102 |
| 🇨🇦 Canada | Constitution Act 1982 | 463 |
| **Total** | | **2,859** |

---

## 🛠️ Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| Embeddings | `sentence-transformers` (all-MiniLM-L6-v2) | Free, CPU-friendly, 384 dims |
| Vector DB | ChromaDB | Simple, local, persistent |
| LLM | Ollama (Llama 3.1) | Free, local, no API costs |
| PDF parsing | PyPDF2 | Extracts text with page numbers |
| UI | Streamlit | Fast to build, looks decent |
| Testing | pytest | Catches bugs before they ship |
| Language | Python 3.9+ | — |
 ---
 
## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.ai/download) installed
- Visual C++ Redistributable ([Windows only](https://aka.ms/vs/17/release/vc_redist.x64.exe))
- ~4 GB RAM

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/constitutional-rag-qa.git
cd constitutional-rag-qa

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\Activate.ps1

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# 1. Add PDFs to data/documents/


# 2. Ingest documents (load + chunk)
python src/ingest.py

# 3. Create embeddings + store in ChromaDB
python src/embed_store.py


# 4. Pull the LLM model (in a separate terminal)
ollama pull llama3.1
ollama serve

# 5. Test retrieval
python src/retrieve.py

# 6. Test answer generation
python src/generate.py

# 7. Launch the UI
streamlit run app.py
Then open http://localhost:8501 in your browser.
```

## 💬 Example Queries
Try asking things like:

 - "What fundamental rights do citizens have?"
 - "How is the president elected?"
 - "What's the process to amend the constitution?"
 - "What emergency powers exist?"
 - "How are judges appointed?"

And out-of-scope questions like "What's the recipe for pizza?" will get refused.


## ⚙️ Configuration

Everything lives in config/config.yaml. The important bits:

|Setting	| Default |	What it does|
|--------|---------|-------------|
|chunk_size |	500 |	Characters per chunk|
|chunk_overlap |	50 |	Overlap between chunks|
|top_k |	3 |	How many chunks to retrieve|
|similarity_threshold |	0.5 |	Below this = "I don't know"|
|llm.model |	llama3.1 |	Which LLM to use|
|llm.temperature |	0.1 |	Lower = more factual|

## 📊 Evaluation
I wrote 30 test questions across 8 categories. The system measures:

 - Hit rate — did search find the right document? (target: ≥80%)
 - Refusal rate — does it refuse on unrelated questions? (target: ≥80%)
 - Citation rate — does every answer have sources?

```bash
python src/eval.py
```

## 🐛 Problems I Ran Into (and how I fixed them)

| Problem |	Fix  |
|--------|------|
| Windows long paths |	Moved project to C:\rag_project |
|PyTorch DLL error |	Installed VC++ Redistributable |
| Pakistan PDF encrypted |	pip install pycryptodome |
| Empty PDF text |	Switched to text-based PDFs |
| Slow downloads |	Used Aliyun mirror for pip |

---

## Project Structure
```
constitutional-rag-qa/
├── config/
│   ├── config.yaml           # All settings
│   └── eval_questions.json   # 30 test questions
├── data/
│   ├── documents/            # Source PDFs
│   └── processed/            # Chunk metadata
├── src/
│   ├── ingest.py             # Load & chunk PDFs
│   ├── embed_store.py        # Embeddings + ChromaDB
│   ├── retrieve.py           # Semantic search
│   ├── generate.py           # LLM answers
│   ├── eval.py               # Evaluation suite
│   └── utils.py              # Shared utilities
├── tests/                    # Unit tests
├── scripts/                  # Setup helpers
├── app.py                    # Streamlit UI
├── Makefile                  # Shortcut commands
├── requirements.txt
└── README.md
```

##🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```
