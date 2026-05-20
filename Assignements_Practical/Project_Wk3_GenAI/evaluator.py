"""Text-to-SQL Evaluation Framework based on evaluation_framework.md."""
import re
import time
import statistics
from typing import Dict, Any, List, Tuple
from enum import Enum
from dataclasses import dataclass, field
from sql_generator import generate_sql, safe_sql_check
from executor import QueryExecutor
from validator import ErrorType, classify_error, validate_query

def normalize_sql(sql: str) -> str:
    """Normalize SQL for comparison (lowercase, remove extra whitespace, standardize aliases)."""
    sql = sql.lower().strip()
    sql = re.sub(r'\s+', ' ', sql)
    # Remove alias placeholders that might differ
    sql = re.sub(r'\b[a-z]\.', '', sql)
    return sql.strip()


def parse_sql_components(sql: str) -> Dict[str, List[str]]:
    """Parse SQL into components for component-level accuracy."""
    import re
    components = {
        'tables': [],
        'columns': [],
        'joins': [],
        'where_conditions': [],
        'aggregations': []
    }

    # Extract tables from FROM and JOIN clauses
    from_match = re.search(r'from\s+(\w+)', sql.lower())
    if from_match:
        components['tables'].append(from_match.group(1).strip('"'))

    join_pattern = re.findall(r'join\s+(\w+)', sql.lower())
    components['tables'].extend([t.strip('"') for t in join_pattern])

    # Extract columns from SELECT
    select_match = re.search(r'select\s+(.*?)\s+from', sql.lower(), re.DOTALL)
    if select_match:
        cols = select_match.group(1).split(',')
        components['columns'] = [c.strip().strip('"') for c in cols]

    # Extract JOIN conditions
    join_ons = re.findall(r'join\s+\w+\s+on\s+(.+?)(?:\s+(?:join|where|group|order|limit|$))', sql.lower())
    components['joins'] = [j.strip() for j in join_ons]

    # Extract WHERE conditions
    where_match = re.search(r'where\s+(.+?)(?:\s+group\s+by|\s+order\s+by|\s+limit|$)', sql.lower())
    if where_match:
        components['where_conditions'] = [where_match.group(1).strip()]

    # Extract aggregations
    aggs = re.findall(r'(count|sum|avg|max|min)\s*\(', sql.lower())
    components['aggregations'] = aggs

    return components


def component_accuracy(generated_sql: str, ground_truth_sql: str) -> Dict[str, float]:
    """Calculate component-level accuracy."""
    gen = parse_sql_components(generated_sql)
    gt = parse_sql_components(ground_truth_sql)
    results = {}
    for comp in ['tables', 'columns', 'joins', 'where_conditions', 'aggregations']:
        gen_set = set(gen[comp])
        gt_set = set(gt[comp])
        if gt_set:
            correct = len(gen_set.intersection(gt_set))
            total = len(gt_set)
            results[comp] = min(100.0, (correct / total) * 100)
        else:
            results[comp] = 100.0 if not gen_set else 0.0
    return results


def execution_match(generated_sql: str, ground_truth_sql: str, executor: QueryExecutor) -> Tuple[bool, List[Any], List[Any]]:
    """Check if generated SQL produces the same results as ground truth."""
    try:
        gen_result = executor.execute(generated_sql)
        gt_result = executor.execute(ground_truth_sql)

        gen_rows = gen_result['result']
        gt_rows = gt_result['result']

        if gen_result['status'] != 'success' and gt_result['status'] != 'success':
            return True, gen_rows, gt_rows

        if len(gen_rows) != len(gt_rows):
            return False, gen_rows, gt_rows

        if not gen_rows and not gt_rows:
            return True, gen_rows, gt_rows

        # Compare sorted results
        gen_sorted = sorted(gen_rows, key=lambda x: str(x))
        gt_sorted = sorted(gt_rows, key=lambda x: str(x))

        for gen_row, gt_row in zip(gen_sorted, gt_sorted):
            for key in gt_row:
                gen_val = gen_row.get(key)
                gt_val = gt_row.get(key)
                if isinstance(gen_val, float) and isinstance(gt_val, float):
                    if abs(gen_val - gt_val) > 1e-6:
                        return False, gen_rows, gt_rows
                elif str(gen_val) != str(gt_val):
                    return False, gen_rows, gt_rows
        return True, gen_rows, gt_rows
    except Exception as e:
        return False, [], []


def exact_match(generated_sql: str, ground_truth_sql: str) -> bool:
    """Check exact match after normalization."""
    return normalize_sql(generated_sql) == normalize_sql(ground_truth_sql)


@dataclass
class EvaluationResult:
    query_id: int
    question: str
    generated_sql: str
    ground_truth_sql: str
    exact_match: bool = False
    execution_match: bool = False
    execution_success: bool = False
    error_type: ErrorType = None
    generation_time_ms: float = 0.0
    component_accuracy: Dict[str, float] = field(default_factory=dict)
    result_gen: List[Dict] = field(default_factory=list)
    result_gt: List[Dict] = field(default_factory=list)


class TextToSQLEvaluator:
    """Evaluator for Text-to-SQL system."""

    def __init__(self, executor: QueryExecutor):
        self.executor = executor
        self.results: List[EvaluationResult] = []

    def evaluate(self, test_cases: List[Dict]) -> Dict[str, Any]:
        """Run full evaluation suite."""
        for case in test_cases:
            result = self._evaluate_single(case)
            self.results.append(result)
        return self._compute_metrics()

    def _evaluate_single(self, case: Dict) -> EvaluationResult:
        """Evaluate a single test case."""
        start_time = time.time()
        generated_sql = case['sql']
        ground_truth = case['ground_truth']
        gen_time = (time.time() - start_time) * 1000

        # Exact match
        is_exact = exact_match(generated_sql, ground_truth)

        # Execute and compare
        exec_match, gen_rows, gt_rows = execution_match(generated_sql, ground_truth, self.executor)

        # Component accuracy
        comp_acc = component_accuracy(generated_sql, ground_truth)

        # Execution success
        exec_success = True
        error_type = ErrorType.NONE
        if not safe_sql_check(generated_sql):
            error_type = ErrorType.PERMISSION
            exec_success = False
        else:
            res = self.executor.execute(generated_sql)
            exec_success = res['status'] == 'success'
            if res['status'] != 'success':
                error_type = classify_error(res.get('error', ''))

        return EvaluationResult(
            query_id=case['id'],
            question=case['question'],
            generated_sql=generated_sql,
            ground_truth_sql=ground_truth,
            exact_match=is_exact,
            execution_match=exec_match,
            execution_success=exec_success,
            error_type=error_type,
            generation_time_ms=gen_time,
            component_accuracy=comp_acc,
            result_gen=gen_rows,
            result_gt=gt_rows,
        )

    def _compute_metrics(self) -> Dict[str, Any]:
        """Compute overall metrics from results."""
        if not self.results:
            return {}

        total = len(self.results)
        exact_matches = sum(1 for r in self.results if r.exact_match)
        exec_matches = sum(1 for r in self.results if r.execution_match)
        exec_successes = sum(1 for r in self.results if r.execution_success)

        # Component accuracy averages
        comp_acc = {k: [] for k in ['tables', 'columns', 'joins', 'where_conditions', 'aggregations']}
        for r in self.results:
            for k, v in r.component_accuracy.items():
                comp_acc[k].append(v)

        avg_comp_acc = {k: round(sum(v)/len(v), 2) if v else 0 for k, v in comp_acc.items()}

        return {
            'total_queries': total,
            'exact_match_rate': round(exact_matches / total * 100, 2),
            'execution_match_rate': round(exec_matches / total * 100, 2),
            'execution_success_rate': round(exec_successes / total * 100, 2),
            'component_accuracy': avg_comp_acc,
            'average_latency': round(statistics.mean([r.generation_time_ms for r in self.results]), 2),
            'error_breakdown': self._error_breakdown()
        }

    def _error_breakdown(self) -> Dict[str, int]:
        """Breakdown of error types."""
        errors = {}
        for r in self.results:
            if r.error_type and r.error_type != ErrorType.NONE:
                key = r.error_type.value
                errors[key] = errors.get(key, 0) + 1
        return errors

    def generate_report(self) -> str:
        """Generate a human-readable evaluation report."""
        metrics = self._compute_metrics()
        report = [
            "# Text-to-SQL Evaluation Report",
            f"\nTotal Queries: {metrics['total_queries']}",
            f"Exact Match Rate: {metrics['exact_match_rate']}%",
            f"Execution Match Rate: {metrics['execution_match_rate']}%",
            f"Execution Success Rate: {metrics['execution_success_rate']}%",
            f"Average Generation Latency: {metrics['average_latency']}ms",
            "\n## Component Accuracy",
        ]
        for k, v in metrics['component_accuracy'].items():
            report.append(f"- {k}: {v}%")

        report.append("\n## Error Breakdown")
        if metrics['error_breakdown']:
            for k, v in metrics['error_breakdown'].items():
                report.append(f"- {k}: {v}")
        else:
            report.append("No errors detected.")

        return "\n".join(report)
