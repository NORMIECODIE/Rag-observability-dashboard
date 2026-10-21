import time

from app.observability.tracing import span


trace = []

with span("test_operation", trace):
    time.sleep(0.2)


print("\nTrace:")
print(trace)