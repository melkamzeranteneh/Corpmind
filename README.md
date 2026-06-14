# Corpmind: Corporate Knowledge Base Assistant (Advanced RAG vs Basic RAG)

A production-quality AI-powered knowledge base assistant that compares **Basic RAG** and **Advanced RAG** architectures. This project demonstrates cutting-edge techniques in Retrieval-Augmented Generation, including GraphRAG, Corrective RAG (CRAG), and agentic orchestration with LangGraph.

## 🚀 Overview

Corpmind is designed to help organizations leverage their internal documentation more effectively. It provides two distinct retrieval strategies to show the evolution from simple vector search to complex, stateful retrieval pipelines.

### **1. Basic RAG Pipeline**
*   **Chunking**: Fixed-size recursive character splitting.
*   **Vector Store**: ChromaDB for semantic indexing.
*   **Retrieval**: Top-K similarity search.
*   **Generation**: Direct context-to-answer synthesis using Mistral Large.

### **2. Advanced RAG Pipeline (Agentic GraphRAG)**
*   **Orchestration**: Managed by **LangGraph** as a stateful, cyclic workflow.
*   **Parent-Child Chunking**: Retrieves granular child chunks but provides full parent context to the LLM for better coherence.
*   **Query Expansion**: Rewrites and expands user queries to handle linguistic variations.
*   **Hybrid Retrieval**:
    *   **Vector Search**: Multi-query retrieval from ChromaDB.
    *   **Graph Retrieval**: Entity & relationship traversal using **Neo4j** (GraphRAG).
*   **Corrective RAG (CRAG)**: An evaluator node grades retrieval quality. If relevance is low, the system triggers query refinement or fallbacks.
*   **Re-ranking**: Uses an LLM-based scoring system (mimicking BGE-Reranker) to prioritize the most relevant snippets.

## 🛠️ Tech Stack

*   **LLM**: Mistral AI (Mistral Large 2)
*   **Frameworks**: LangChain, LangGraph, FastAPI
*   **Databases**: 
    *   **ChromaDB** (Vector Database)
    *   **Neo4j** (Graph Database)
*   **Frontend**: React, TypeScript, Tailwind CSS, Lucide Icons
*   **Processing**: PyMuPDF, Unstructured

## 📁 Project Structure

```text
corpmind/
├── backend/
│   ├── app/
│   │   ├── api/                # FastAPI Routers & Endpoints
│   │   ├── core/               # Configuration (Pydantic Settings)
│   │   ├── services/           # Business Logic
│   │   │   ├── rag_basic.py    # Basic RAG Implementation
│   │   │   └── rag_advanced/   # LangGraph Advanced Workflow
│   │   ├── db/                 # DB Utils (Chroma & Neo4j)
│   │   ├── ingestion/          # Vector & Graph Ingestors
│   │   └── evaluation/         # RAG Benchmarking Pipeline
│   └── requirements.txt        # Backend dependencies
├── frontend/                   # React/Vite/TS Frontend
├── data/                       # Sample corporate documents (.md)
└── README.md                   # You are here
```

## ⚙️ Setup Instructions

### 1. Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Neo4j (Local Desktop or AuraDB Cloud)
*   Mistral API Key

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:
```env
MISTRAL_API_KEY=your_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
CHROMA_DB_PATH=./chroma_db
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Run the Application
**Start Backend:**
```bash
cd backend
python -m app.main
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

## 📊 Evaluation & Benchmarking

The system includes a built-in evaluation pipeline that tests both RAG modes against 10 specific question types:
*   **Factual**: Direct retrieval.
*   **Paraphrased**: Testing query expansion robustness.
*   **Multi-hop**: Requires following relationships (GraphRAG).
*   **Unanswerable**: Testing hallucination resistance.

Click **"Run Benchmarks"** in the dashboard to see a side-by-side performance analysis with automated LLM grading.
