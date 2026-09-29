from app.observability.trace_store import save_trace

save_trace(
    trace_id="test-trace-123",
    question="MongoDB test question",
    answer="MongoDB test answer",
    spans=[
        {
            "name": "test",
            "status": "ok",
            "duration_ms": 10
        }
    ],
    status="success"
)

print("Test trace saved!")