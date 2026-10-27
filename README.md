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

*Some supporting files and modules may be omitted from this simplified structure.*

## Getting Started

### Prerequisites

Install or configure the following:

- Python 3.10 or a compatible Python version
- Node.js and npm
- Docker Desktop, if running Qdrant through Docker
- MongoDB
- A Google Gemini API key

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Rag-observability-dashboard
```

Replace the placeholder with your actual GitHub repository URL.

### 2. Configure the Backend

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment.

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

This assumes a `requirements.txt` file is present in the backend directory. If dependencies are managed another way, install them using the project's actual dependency configuration.

### 3. Configure Environment Variables

Create a `.env` file in the backend directory and configure the environment variables required by your application.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Configure the MongoDB and Qdrant connection settings required by your code as well.

**Security:** Never commit `.env` files, API keys, database credentials, or other secrets to GitHub.

### 4. Start the Required Services

Start MongoDB and Qdrant using your local installations or Docker configuration.

Verify that both services are reachable using the connection settings configured in your backend.

### 5. Run the Backend

From the `backend/` directory, with the virtual environment activated:

```bash
uvicorn app.main:app --reload
```

The backend should be available at:

- API: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### 6. Run the Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, typically:

`http://localhost:5173`

Ensure the frontend API configuration points to the running backend.

## Evaluation Workflow

The evaluation pipeline uses a dataset of test questions to assess RAG answer quality.

Run it from the `backend/` directory:

```bash
python -m evaluation.run_evaluation
```

The script reads the evaluation dataset, reuses saved results, evaluates remaining questions, and updates:

```text
backend/evaluation/evaluation_report.json
```

### Evaluation Metrics

| Metric | Description |
|---|---|
| Faithfulness | Measures whether the answer is supported by the retrieved context. |
| Relevance | Measures how well the answer addresses the question. |
| Completeness | Measures how thoroughly the answer covers the question. |
| RAG Latency | Time taken to execute the RAG request. |
| Judge Latency | Time taken by the LLM judge to evaluate the answer. |
| Estimated Cost | Estimated generation cost when the required usage and pricing data are available. |

**Cost reporting note:** Historical evaluation results may not contain cost information. The total cost is reported as unavailable unless valid numeric cost data exists for every result included in the report.

## API Endpoints

The backend provides API routes for trace inspection, evaluation results, and dashboard metrics.

| Endpoint | Purpose |
|---|---|
| `GET /traces` | Retrieve trace records. |
| `GET /traces/{trace_id}` | Retrieve a trace by its ID. |
| `GET /traces/{trace_id}/details` | Retrieve detailed trace information. |
| `GET /metrics/overview` | Retrieve dashboard overview metrics. |
| `GET /metrics/latency` | Retrieve latency metrics. |
| `GET /metrics/evaluation` | Retrieve evaluation summary metrics. |
| `GET /metrics/evaluation/results` | Retrieve evaluation results. |

These endpoints assume the routes are registered under the listed paths in the current backend configuration. Check `/docs` for the definitive API schema.

## Future Improvements

- Add retrieval precision and recall evaluation.
- Track token usage and cost per request with provider-specific pricing.
- Add filters for trace IDs, latency, status, and evaluation scores.
- Detect low-quality retrieval and potentially hallucinated answers.
- Add configurable evaluation datasets and scheduled evaluations.
- Support comparisons between embedding models, chunking strategies, and retrieval configurations.
- Add trace-level drill-down views and improved error analysis.
- Add automated tests, CI workflows, and deployment configuration.

## Why This Project?

RAG applications require more than a working retrieval pipeline. They need ways to understand retrieval quality, inspect model behavior, measure latency, track costs, and evaluate answer reliability.

This project explores how observability and evaluation can make RAG systems easier to debug, measure, and improve.

## Contributing

Contributions and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes and test them.
4. Submit a pull request describing the changes.

## License

A license has not yet been specified. Add a `LICENSE` file and update this section before distributing the project under an open-source license.

---

**Built as a hands-on project in RAG systems, LLM evaluation, observability, and full-stack development.**
