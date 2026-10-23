import uuid

from app.observability.trace_store import save_trace

trace_id = f"test-trace-{uuid.uuid4()}"

# Saving the trace
save_trace(
    trace_id=trace_id,
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

# Printing the trace
print(f"Test trace saved! Trace ID: {trace_id}")