#!/bin/bash
# One-command setup for RAG Constitutional QA System

echo "========================================="
echo "RAG Constitutional QA System - Setup"
echo "========================================="

# Create virtual environment
echo -e "\n📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo -e "\n📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create directories
echo -e "\n📁 Creating directories..."
mkdir -p data/documents
mkdir -p data/processed
mkdir -p logs

# Download embedding model (triggers first-time download)
echo -e "\n🧮 Downloading embedding model (this may take a minute)..."
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

echo -e "\n✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Add PDF documents to data/documents/"
echo "  2. Run: make ingest"
echo "  3. Run: make embed"
echo "  4. Run: make test-retrieval"
echo "  5. Run: make ui"