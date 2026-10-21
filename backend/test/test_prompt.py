from app.rag.prompt import build_prompt


query = "What did Rutherford propose about the atom?"

contexts = [
    {
        "page": 2,
        "text": "Rutherford proposed a very small, dense, positively charged nucleus at the centre of the atom."
    },
    {
        "page": 2,
        "text": "Most alpha particles passed straight through the gold foil without being deflected."
    }
]


prompt = build_prompt(query, contexts)

print(prompt)