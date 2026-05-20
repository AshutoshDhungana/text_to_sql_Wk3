"""SQL execution with retry logic (Task 3: 1 retry, Task 4: 3 retries)."""
import time
import logging
from typing import Dict, Any, List, Tuple
import psycopg2
from database import get_connection, safe_sql_check

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class QueryExecutor:
    """Executes SQL queries against PostgreSQL with retry logic."""

    def __init__(self, max_retries: int = 1):
        self.max_retries = max_retries
        self.logs = []

    def execute(self, sql: str, question_id: int = 0) -> Dict[str, Any]:
        """Execute SQL with retry logic."""
        if not safe_sql_check(sql):
            return {
                "sql": sql,
                "result": [],
                "status": "blocked",
                "error": "Unsafe SQL detected (only SELECT allowed)",
                "attempts": 0,
                "execution_time_ms": 0,
            }

        start = time.time()
        attempts = 0
        result_data = []
        last_error = None

        while attempts <= self.max_retries:
            try:
                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute(sql)
                    if cur.description:
                        rows = cur.fetchall()
                        columns = [desc[0] for desc in cur.description]
                        result_data = [{k: v for k, v in zip(columns, row)} for row in rows]
                    else:
                        result_data = []
                        columns = []
                conn.close()
                return {
                    "sql": sql,
                    "result": result_data,
                    "columns": columns if result_data else [],
                    "status": "success",
                    "error": None,
                    "attempts": attempts,
                    "execution_time_ms": round((time.time() - start) * 1000, 2),
                }

            except psycopg2.Error as e:
                last_error = str(e)
                attempts += 1
                if attempts > self.max_retries:
                    break
                logger.warning(f"Q{question_id} attempt {attempts} failed: {last_error}. Retrying...")
                continue
            except Exception as e:
                last_error = str(e)
                break

        return {
            "sql": sql,
            "result": [],
            "status": "failed",
            "error": last_error,
            "attempts": attempts,
            "execution_time_ms": round((time.time() - start) * 1000, 2),
        }

    def execute_batch(self, queries: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Execute multiple queries and return results."""
        results = []
        for q in queries:
            res = self.execute(q["sql"], q.get("id", 0))
            results.append({
                "id": q.get("id", 0),
                "question": q.get("question", ""),
                **res,
            })
        return results


def test_connection():
    """Test database connectivity."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        conn.close()
        return True, version
    except Exception as e:
        return False, str(e)
