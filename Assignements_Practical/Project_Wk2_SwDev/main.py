"""
main.py — Application Entry Point
====================================
Creates the FastAPI app, registers routers, and starts Uvicorn.

Run with:
    uvicorn main:app --reload
Then visit:
    http://localhost:8000/docs  ← automatic Swagger UI
"""

from fastapi import FastAPI

import customers, dashboard
from logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title="Classic Models API",
    description=(
        "A layered FastAPI application built on the Classic Models dataset.\n\n"
        "**Task 2** — Full Customer CRUD API with related orders & payments.\n\n"
        "**Task 3** — Concurrent dashboard endpoint using `asyncio.gather()` "
        "(Twelve-Factor App, Factor VIII: Concurrency)."
    ),
    version="1.0.0",
)

# Register routers
# Dashboard router first so /customers/count is matched before /customers/{id}
app.include_router(dashboard.router)
app.include_router(customers.router)

logger.info("FastAPI application started. Visit /docs for Swagger UI.")


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Classic Models API is running.",
        "docs": "/docs",
        "redoc": "/redoc",
    }
