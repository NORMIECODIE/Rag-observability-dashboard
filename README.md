# RAG Observability Dashboard

**Monitor, trace, and evaluate Retrieval-Augmented Generation (RAG) pipelines.**

A full-stack observability dashboard designed to make RAG applications easier to debug, monitor, and evaluate. It tracks the RAG execution flow, records traces, measures latency and estimated generation costs, and evaluates answer quality using LLM-based evaluation metrics.

The goal is to understand not only *what answer a RAG system produces*, but also *how it produces that answer, how long it takes, and how reliable the answer is*.

## Overview

Retrieval-Augmented Generation (RAG) combines information retrieval with large language models (LLMs). However, a RAG application can produce incorrect answers because of poor retrieval, irrelevant context, or generation errors.

This project provides an observability layer for inspecting and evaluating these workflows.

### Key Features

- **RAG Tracing:** Track queries and inspect execution traces to understand the RAG pipeline.
- **Retrieval Inspection:** Examine retrieved document chunks and their relevance to a query.
- **Latency Monitoring:** Measure RAG execution time and LLM evaluation time.
- **Cost Tracking:** Calculate and record estimated LLM generation costs using token usage and model pricing.
- **LLM-Based Evaluation:** Evaluate generated answers using faithfulness, relevance, and completeness scores.
- **Evaluation Reports:** Store evaluation results and calculate aggregate metrics.
- **Interactive Dashboard:** Visualize performance metrics and inspect recent traces through a React-based interface.
- **Trace Debugging:** Inspect trace records to investigate pipeline behavior and potential failures.

## Architecture

```text
                 User Query
                     |
                     v
          +----------------------+
          |     FastAPI Backend  |
          +----------------------+
                     |
                     v
          +----------------------+
          |    RAG Pipeline      |
          +----------------------+
              |             |
              v             v
       Document Search    Gemini LLM
         (Qdrant)             |
              |               |
              +-------+-------+
                      |
                      v
                Generated Answer
                      |
                      v
          +----------------------+
          |  Trace & Metrics     |
          |  Collection          |
          +----------------------+
                      |
           +----------+-----------+
           |                      |
           v                      v
    MongoDB Trace Data      Evaluation Reports
           |                      |
           +----------+-----------+
                      |
                      v
          +----------------------+
          |   FastAPI Endpoints  |
          +----------------------+
                      |
                      v
          +----------------------+
          | React Dashboard      |
          | Metrics & Traces     |
          +----------------------+
```

*Note: The diagram represents the high-level workflow; exact storage and instrumentation details depend on the current implementation.*

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, FastAPI |
| LLM | Google Gemini |
| Vector Database | Qdrant |
| Trace Storage | MongoDB |
| Document Processing | PyPDF |
| Evaluation | Custom evaluation pipeline and LLM judge |
| Data Visualization | Recharts |
| API Communication | Axios |
| Version Control | Git and GitHub |

## How It Works

### 1. Query Processing

A user submits a question to the RAG pipeline. The application retrieves relevant document chunks from the vector database.

### 2. Answer Generation

The retrieved context is passed to the Gemini language model to generate an answer grounded in the available documents.

### 3. Trace Collection

The application records trace information that can be inspected to understand the execution flow, retrieved context, generation behavior, and performance.

### 4. Performance Monitoring

The backend exposes metrics such as request latency, evaluation latency, and estimated generation cost where the required data is available.

### 5. Answer Evaluation

An LLM-based judge evaluates generated answers using three metrics:

- **Faithfulness:** How well the answer is supported by the retrieved context.
- **Relevance:** How closely the answer addresses the user's question.
- **Completeness:** How thoroughly the answer addresses the question.

The evaluation pipeline saves individual scores and calculates aggregate metrics for reporting.

## Project Structure

```text
Rag-observability-dashboard/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes_evaluation.py
│   │   │   └── routes_traces.py
│   │   ├── observability/
│   │   │   └── check_traces.py
│   │   ├── rag/
│   │   │   ├── ingestion.py
│   │   │   └── pipeline.py
│   │   └── main.py
│   ├── evaluation/
│   │   ├── test_questions.json
│   │   ├── run_evaluation.py
│   │   ├── check_costs.py
│   │   └── evaluation_report.json
│   └── documents/
└── frontend/
    ├── public/
    ├── src/
    │   ├── assets/
    │   ├── App.jsx
    │   ├── App.css
    │   ├── api.js
    │   ├── index.css
    │   └── main.jsx
    ├── package.json
    └── vite.config.js
```


