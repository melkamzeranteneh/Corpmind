# Corpmind: Corporate Knowledge Base Assistant

A production-quality RAG system that demonstrates the power of **Advanced RAG (GraphRAG + LangGraph)** compared to **Basic RAG**.

## Features

- **Basic RAG**: Fixed-size chunking, ChromaDB vector search, Mistral Large generation.
- **Advanced RAG**:
  - **Parent-Child Chunking**: Better context retention.
  - **Query Expansion**: Multi-query variations for robust retrieval.
  - **Hybrid Retrieval**: Combines Vector search (Chroma) with Graph search (Neo4j).
  - **Corrective RAG (CRAG)**: Evaluates retrieval quality and retries if necessary.
  - **Re-ranking**: Prioritizes the most relevant context before generation.
- **Agentic Orchestration**: Managed by **LangGraph** for stateful, cyclic workflows.
- **Knowledge Graph**: Entity and relationship extraction using **Mistral** and **Neo4j**.
- **Evaluation Pipeline**: Benchmarks both systems across 10+ questions with automated comparison.

## Tech Stack

- **Backend**: FastAPI, LangChain, LangGraph
- **Frontend**: React, TypeScript, Tailwind CSS
- **LLM**: Mistral AI (Mistral Large)
- **Databases**: ChromaDB (Vector), Neo4j (Graph)

## Prerequisites

- Python 3.10+
- Node.js 18+
- Mistral API Key
- Neo4j Instance (Local or AuraDB)

## Setup Instructions

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory:

```env
MISTRAL_API_KEY=your_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
CHROMA_DB_PATH=./chroma_db
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

### 3. Running the Application

**Start the Backend:**
```bash
cd backend
python app/main.py
```

**Start the Frontend:**
```bash
cd frontend
npm run dev
```

## Usage

1.  Open `http://localhost:3000`.
2.  Click **"Run Ingestion"** to process the sample documents in the `data/` folder.
3.  Ask questions in the search bar to see side-by-side results.
4.  Click **"Run Benchmarks"** to see the automated evaluation of both systems.

## Evaluation Questions

The system is pre-configured with 10 questions covering:
- Factual queries
- Paraphrased queries
- Multi-hop reasoning (Graph required)
- Relationship-based queries
- Unanswerable queries
