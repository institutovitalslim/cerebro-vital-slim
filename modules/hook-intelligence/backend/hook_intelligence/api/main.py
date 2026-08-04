from fastapi import FastAPI

app = FastAPI(title="Hook Intelligence Engine", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ready",
        "service": "hook-intelligence",
        "version": "0.1.0",
        "ai_enabled": False,
    }
