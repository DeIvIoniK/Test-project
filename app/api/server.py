from fastapi import FastAPI

app = FastAPI(title="AA Recovery Support Bot API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
