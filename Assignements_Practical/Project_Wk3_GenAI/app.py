"""Task 4: Mini SQL Agent - FastAPI endpoint.

POST /agent/sql
Input: {"question": "How many shipped orders are from USA customers?"}
Output: {"sql": "...", "result": ..., "summary": "...", "status": "success"}
"""
import os
import time
import logging
from typing import Any, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sql_generator import generate_sql, parse_decomposition
from executor import QueryExecutor, test_connection
from validator import validate_query, ValidationResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track stats
request_count = 0
total_generation_time = 0.0

app = FastAPI(title="Mini SQL Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    sql: str
    result: Any
    summary: str
    status: str
    attempts: int
    execution_time_ms: float


# Load decompositions into memory
decompositions = parse_decomposition()


def find_best_decomposition(question: str) -> Dict[str, Any]:
    """Find the best matching decomposition for a question."""
    # Simple matching by looking at keywords in the question
    lower_q = question.lower()

    for dec in decompositions:
        # Check if any table mentioned
        tables = dec.get("Tables", [])
        if tables:
            for table in tables:
                if table.lower() in lower_q:
                    return dec

    # Fallback: return first decomposition
    if decompositions:
        return decompositions[0]
    return {}


def nl_summary(question: str, result: Any) -> str:
    """Generate a simple natural language summary of the result."""
    if not result:
        return f"No results found for: {question}"
    if isinstance(result, list) and len(result) > 0:
        first = result[0]
        if isinstance(first, dict):
            # If single value like COUNT(*)
            if len(first) == 1:
                key = list(first.keys())[0]
                val = first[key]
                return f"The answer is {val} for: {question}"
            # Multi-column
            return f"Found {len(result)} result(s) for: {question}"
        return f"Results: {result}"
    return f"Result for '{question}': {result}"


@app.post("/agent/sql", response_model=QueryResponse)
async def agent_sql(request: QueryRequest):
    """Mini SQL Agent: Understand -> Generate -> Execute -> Retry (max 3) -> Summarize."""
    global request_count, total_generation_time
    question = request.question
    start_time = time.time()
    request_count += 1

    # Step 1: Decompose question
    dec = find_best_decomposition(question)

    # Step 2: Validate
    if not dec:
        return QueryResponse(
            sql="",
            result=None,
            summary=f"Could not decompose question: {question}",
            status="failed",
            attempts=0,
            execution_time_ms=0,
        )

    # Step 3: Generate SQL
    try:
        sql = generate_sql(dec)
    except Exception as e:
        logger.error(f"SQL generation failed: {e}")
        return QueryResponse(
            sql="",
            result=None,
            summary=f"SQL generation failed for: {question}",
            status="failed",
            attempts=0,
            execution_time_ms=0,
        )

    # Step 4: Validate
    val = validate_query(sql)
    if not val.valid:
        return QueryResponse(
            sql=sql,
            result=None,
            summary=f"Query validation failed: {val.error_message}",
            status="failed",
            attempts=0,
            execution_time_ms=0,
        )

    # Step 5: Execute with retry (max 3)
    executor = QueryExecutor(max_retries=3)
    res = executor.execute(sql)

    # Step 6: Prepare response
    summary = nl_summary(question, res["result"])
    status = res["status"]
    attempts = res.get("attempts", 0)
    exec_time = res.get("execution_time_ms", (time.time() - start_time) * 1000)
    total_generation_time += exec_time

    return QueryResponse(
        sql=sql,
        result=res["result"],
        summary=summary,
        status=status,
        attempts=attempts,
        execution_time_ms=exec_time,
    )


@app.get("/health")
async def health():
    ok, msg = test_connection()
    return {"status": "healthy" if ok else "unhealthy", "db": msg, "requests_handled": request_count}


@app.get("/")
async def root():
    return {"message": "Mini SQL Agent API", "docs": "/docs"}
