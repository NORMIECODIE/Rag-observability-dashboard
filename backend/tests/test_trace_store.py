from app.observability.mongodb import traces_collection


print("Database:", traces_collection.database.name)
print("Collection:", traces_collection.name)

print("\nSearching for trace...")

trace = traces_collection.find_one(
    {
        "trace_id": "69f525b1-d980-4e07-8ad0-76e949bdfee9"
    }
)

if trace:
    print("\nTrace found!")
    print("--------------------------------")
    print("Trace ID:", trace.get("trace_id"))
    print("Question:", trace.get("question"))
    print("Answer:", trace.get("answer"))
    print("Status:", trace.get("status"))
    print("Total Latency:", trace.get("total_latency_ms"), "ms")

    print("\nSpans:")

    for span in trace.get("spans", []):
        print(
            f"- {span.get('name')} | "
            f"Status: {span.get('status')} | "
            f"Duration: {span.get('duration_ms')} ms"
        )

else:
    print("\nNo trace found.")