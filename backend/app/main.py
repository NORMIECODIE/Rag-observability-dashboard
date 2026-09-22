from fastapi import FastAPI

app = FastAPI(title="RAG Observability API")


@app.get("/")
def root():
    return {"message": "RAG Observability API"}