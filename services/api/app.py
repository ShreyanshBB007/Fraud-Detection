# placeholder small health endpoint
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok", "service": "fraud-capstone-api"}
