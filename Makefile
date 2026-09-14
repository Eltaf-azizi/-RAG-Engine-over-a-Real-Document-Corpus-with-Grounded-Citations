.PHONY: setup ingest test-retrieval eval ui clean help

help:
	@echo "Available commands:"
	@echo "  make setup          - Install dependencies"
	@echo "  make ingest         - Load and chunk documents"
	@echo "  make embed          - Create embeddings and store in Chroma"
	@echo "  make test-retrieval - Test retrieval with sample queries"
	@echo "  make eval           - Run full evaluation suite"
	@echo "  make ui             - Launch Streamlit app"
	@echo "  make test           - Run unit tests"
	@echo "  make clean          - Remove generated files"

setup:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	mkdir -p data/documents data/processed logs

ingest:
	python src/ingest.py

embed:
	python src/embed_store.py

test-retrieval:
	python src/retrieve.py

eval:
	python src/eval.py

ui:
	streamlit run app.py

test:
	pytest tests/ -v

clean:
	rm -rf chroma_db/
	rm -rf data/processed/*
	rm -rf logs/*
	rm -f eval_results.json
	find . -type d -name "__pycache__" -exec rm -rf {} +