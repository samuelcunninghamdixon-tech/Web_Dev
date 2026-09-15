from fastapi import FastAPI

app = FastAPI(title="Scraper Service")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
