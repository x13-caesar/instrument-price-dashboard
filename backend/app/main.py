from fastapi import FastAPI

app = FastAPI(title="Instrument Price Dashboard API")


@app.get("/api/health")
def health():
    return {"status": "ok"}
