from app.llm.client import client


print("Models that support generationContent:\n")

for model in client.models.list():

    if "generateContent" in model.supported_actions:

        print(model.name)