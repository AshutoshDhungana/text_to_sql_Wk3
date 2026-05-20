"""Task 3: Text-to-SQL Pipeline and Query Execution System.

Runs the full pipeline: parse decomposition -> generate SQL -> execute -> evaluate.
Produces a JSON report and scorecard for all 50 benchmark questions.
"""
import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, List

from sql_generator import generate_sql, parse_decomposition, read_sql_file
from executor import QueryExecutor, test_connection
from evaluator import TextToSQLEvaluator
from validator import validate_query, ValidationResult

def run_pipeline(report_path: str = "./evaluation_report.json", scorecard_path: str = "./scorecard.md"):
    print("=" * 60)
    print("Task 3: Text-to-SQL Pipeline Execution")
    print("=" * 60)

    # Step 1: Check database connection
    print("\n[1/5] Checking database connection...")
    ok, msg = test_connection()
    if not ok:
        print(f"ERROR: Cannot connect to database: {msg}")
        print("Please ensure PostgreSQL is running and DB_URL is correct.")
        sys.exit(1)
    print(f"Database connected: {msg}")

    # Step 2: Parse decompositions and read SQL file
    print("\n[2/5] Reading benchmark questions and decompositions...")
    decompositions = parse_decomposition()
    # We already have the SQL queries, use them as ground truth
    ground_truth_queries = read_sql_file("sql_queries.sql")
    print(f"Loaded {len(decompositions)} decompositions and {len(ground_truth_queries)} ground truth SQLs.")

    # Step 3: Generate SQL from decomposition and evaluate
    print("\n[3/5] Generating and executing SQL queries...")
    generated_results = []
    executor = QueryExecutor(max_retries=1)
    total_gen_time = 0

    for i, dec in enumerate(decompositions):
        try:
            start = time.time()
            sql = generate_sql(dec)
            gen_time = (time.time() - start) * 1000
            total_gen_time += gen_time
        except Exception as e:
            print(f"  Q{i+1}: Generation error: {e}")
            sql = ""

        # Execute
        exec_result = executor.execute(sql, question_id=i+1)
        exec_result['id'] = i + 1
        exec_result['question'] = dec.get('Question', f'Question {i+1}')
        generated_results.append(exec_result)

        # Validate
        if sql:
            val = validate_query(sql)
            exec_result['validation'] = {"valid": val.valid, "error": val.error_message}
        else:
            exec_result['validation'] = {"valid": False, "error": "Empty SQL"}

    print(f"Completed {len(generated_results)} queries.")

    # Step 4: Evaluate against ground truth
    print("\n[4/5] Evaluating generated SQL against ground truth...")

    # Prepare evaluation cases
    eval_cases = []
    for i, gt in enumerate(ground_truth_queries):
        if i < len(generated_results):
            eval_cases.append({
                "id": i + 1,
                "question": gt["question"],
                "sql": generated_results[i]["sql"],
                "ground_truth": gt["sql"],
            })

    evaluator = TextToSQLEvaluator(executor)
    metrics = evaluator.evaluate(eval_cases)

    # Step 5: Save report
    print("\n[5/5] Saving evaluation report...")

    report = {
        "task": "Task 3: Text-to-SQL Pipeline",
        "metrics": metrics,
        "per_query_results": [
            {
                "id": r.query_id,
                "question": r.question,
                "generated_sql": r.generated_sql,
                "ground_truth_sql": r.ground_truth_sql,
                "exact_match": r.exact_match,
                "execution_match": r.execution_match,
                "execution_success": r.execution_success,
                "error_type": r.error_type.value if r.error_type else None,
                "generation_time_ms": r.generation_time_ms,
                "component_accuracy": r.component_accuracy,
            }
            for r in evaluator.results
        ],
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Saved JSON report to: {report_path}")

    # Generate scorecard markdown
    scorecard = [
        "# Text-to-SQL Evaluation Scorecard",
        f"\n**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Overall Metrics",
        f"- Total Queries: {metrics['total_queries']}",
        f"- Exact Match Rate: {metrics['exact_match_rate']}%",
        f"- Execution Match Rate: {metrics['execution_match_rate']}%",
        f"- Execution Success Rate: {metrics['execution_success_rate']}%",
        f"- Average Generation Time: {metrics['average_latency']}ms",
        "",
        "### Component Accuracy",
    ]
    for k, v in metrics['component_accuracy'].items():
        scorecard.append(f"- {k}: {v}%")

    scorecard.extend([
        "",
        "### Error Breakdown",
    ])
    if metrics['error_breakdown']:
        for k, v in metrics['error_breakdown'].items():
            scorecard.append(f"- {k}: {v}")
    else:
        scorecard.append("No errors detected.")

    scorecard.extend([
        "",
        "## Per-Query Results",
        "| Q# | Question | Exact | Exec | Status |",
        "|---|---|---|---|---|",
    ])
    for r in evaluator.results:
        status = "✅" if r.execution_success else "❌"
        exact = "✅" if r.exact_match else "❌"
        exec_m = "✅" if r.execution_match else "❌"
        scorecard.append(f"| {r.query_id} | {r.question[:30]}... | {exact} | {exec_m} | {status} |")

    scorecard_md = "\n".join(scorecard)
    with open(scorecard_path, "w", encoding="utf-8") as f:
        f.write(scorecard_md)
    print(f"Saved scorecard to: {scorecard_path}")

    print("\n" + "=" * 60)
    print("Pipeline execution complete!")
    print(f"Exact Match: {metrics['exact_match_rate']}%")
    print(f"Execution Match: {metrics['execution_match_rate']}%")
    print(f"Execution Success: {metrics['execution_success_rate']}%")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
