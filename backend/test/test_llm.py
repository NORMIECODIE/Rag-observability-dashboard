from app.llm import client

response = client.chat.completions.create(
    model="gemini-3.8-flash",
    messages=[
        {
            "role": "user",
            "content": "Explain RAG in one simple sentence."
        }
    ]
)

print(response.choices[0].message.content)