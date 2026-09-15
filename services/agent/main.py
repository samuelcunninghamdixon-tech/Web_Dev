from fastapi import FastAPI

app = FastAPI(title="Agency Agent Service")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
