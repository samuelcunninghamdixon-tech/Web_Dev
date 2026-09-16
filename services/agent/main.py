from fastapi import FastAPI

try:
    from .config import Settings
    from .routes.audit import router as audit_router
    from .routes.codegen import router as codegen_router
    from .routes.slack_hitl import router as slack_router
except ImportError:
    from config import Settings
    from routes.audit import router as audit_router
    from routes.codegen import router as codegen_router
    from routes.slack_hitl import router as slack_router

settings = Settings()
app = FastAPI(title=settings.service_name)

app.include_router(audit_router)
app.include_router(codegen_router)
app.include_router(slack_router)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", **settings.public_metadata()}


@app.get("/ready")
def readiness_check() -> dict:
    return {"status": "ready", "checks": {"configuration": "ok"}, **settings.public_metadata()}
