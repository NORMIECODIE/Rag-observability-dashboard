@'
# RAG Observability Dashboard

A full-stack application for running a Retrieval-Augmented Generation (RAG) pipeline and monitoring its performance, token usage, estimated LLM costs, and evaluation results.

## Features

- RAG pipeline for document retrieval and answer generation.
- Gemini integration for LLM responses.
- Qdrant vector database for semantic retrieval.
- MongoDB for storing trace records.
- Custom tracing for embedding, retrieval, generation, and evaluation stages.
- Observability API for retrieving traces and aggregate metrics.
- Evaluation metrics for retrieval similarity and answer coverage.
- React dashboard with charts and automatic metric refresh.
- Error handling for unavailable backends and missing traces.

## Technology Stack

- Backend: Python, FastAPI
- Frontend: React, Vite
- LLM: Gemini
- Vector database: Qdrant
- Trace storage: MongoDB
- Visualization: Recharts

## Project Structure

```text
rag-observability-dashboard/
├── backend/
│   ├── app/
│   │   ├── evaluation/
│   │   ├── observability/
│   │   ├── rag/
│   │   ├── config.py
│   │   ├── llm.py
│   │   └── main.py
│   ├── test/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── README.md
├── documents/
├── evalution/
└── README.md