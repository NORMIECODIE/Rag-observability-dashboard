
# Day 17 — RAG Retrieval Evaluation

## 1. Objective

Evaluate how chunk size, chunk overlap, and top K affect retrieval performance in the RAG pipeline.

## 2. Experimental Setup

- Document: `What is NLP.pdf`
- Evaluation dataset: `test_questions.json`
- Vector database: Qdrant
- Embedding model: Gemini embedding model
- Similarity threshold: 0.75
- Evaluation metric: Page-match precision proxy
- Unanswerable questions: Excluded from this metric

## 3. Recorded Results

| Chunk Size | Overlap | Top K | Precision |
|---:|---:|---:|---:|
| 500 | 100 | 3 | 0.567 |
| 500 | 100 | 5 | 0.585 |
| 300 | 100 | 3 | 0.728 |
| 300 | 100 | 5 | 0.706 |
| 300 | 50 | 3 | 0.787 |
| 300 | 50 | 5 | 0.783 |

**Note:** These are recorded experimental results. Earlier runs produced different scores for the same nominal configuration, so the comparisons are provisional and should be repeated under controlled conditions.

## 4. Preliminary Findings

1. The best recorded score is 0.787 for chunk size 300, overlap 50, and top K 3.
2. With chunk size 300 and overlap 50, top K 3 scored slightly higher than top K 5.
3. The recorded results suggest that overlap and chunk size may affect retrieval performance.
4. These results do not establish causation because the baseline results varied between runs.

## 5. Metric Limitations

The current metric checks whether a retrieved chunk's page number matches the expected source page.

It does not verify whether the retrieved text actually answers the question. Therefore, it is a page-match proxy rather than a complete measure of retrieval relevance or answer correctness.

Unanswerable questions are excluded, so this evaluation does not measure the system's ability to reject questions that cannot be answered from the documents.

## 6. Next Improvements

1. Repeat experiments with controlled ingestion and evaluation configurations.
2. Record the active Qdrant collection configuration for every run.
3. Add chunk-level relevance labels to the evaluation dataset.
4. Evaluate unanswerable questions separately.
5. Add retrieval metrics such as Recall@K and Mean Reciprocal Rank (MRR).
6. Save results in a machine-readable format for the observability dashboard.

## 7. Conclusion

The evaluation pipeline and embedding cache have been implemented, and multiple retrieval experiments have been recorded. The current preliminary best is chunk size 300, overlap 50, and top K 3, with a page-match precision proxy of 0.787.

Further controlled experiments and stronger relevance metrics are required before selecting a production configuration.
