from app.observability.mongodb import traces_collection


# Printing the database and collection
print("Database:", traces_collection.database.name)
print("Collection:", traces_collection.name)



print("\nSearching for trace...")

# Finding the trace
trace = traces_collection.find_one(
    {
        "trace_id": "7b3ee699-26b9-4e60-8c77-94f1ef16a7ee"
    }
)

# Checking if the trace is found
if trace:
    print("\nTrace found!")
    print("--------------------------------")
    print("Trace ID:", trace.get("trace_id"))
    print("Question:", trace.get("question"))
    print("Answer:", trace.get("answer"))
    print("Status:", trace.get("status"))
    print("Total Latency:", trace.get("total_latency_ms"), "ms")

    print("\nSpans:")

    # Iterating through the spans
    for span in trace.get("spans", []):
        # Printing the spans
        print(
            f"- {span.get('name')} | "
            f"Status: {span.get('status')} | "
            f"Duration: {span.get('duration_ms')} ms"
        )

else:
    # If the trace is not found
    print("\nNo trace found.")