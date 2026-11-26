"""Supervised Visitation Directory API."""

from fastapi import FastAPI
from backend.api.states import router as states_router
from backend.api.counties import router as counties_router
from backend.api.supervisors import router as supervisors_router

app = FastAPI(
    title="Supervised Visitation Directory",
    version="0.1.0",
)

app.include_router(supervisors_router)
app.include_router(states_router)
app.include_router(counties_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
