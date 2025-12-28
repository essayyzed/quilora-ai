from fastapi import FastAPI
from src.api.routes import query

app = FastAPI()

app.include_router(query.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Retrieval-Augmented Generation API!"}