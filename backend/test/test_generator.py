from app.rag.generator import generate_answer


prompt = """
You are a helpful assistant.

Context:
Rutherford proposed a very small, dense, positively charged nucleus
at the centre of the atom.

Question:
What did Rutherford propose about the atom?

Answer:
"""


answer = generate_answer(prompt)

print("\nGenerated Answer:")
print(answer)