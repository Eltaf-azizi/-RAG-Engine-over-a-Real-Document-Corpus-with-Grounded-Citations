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
