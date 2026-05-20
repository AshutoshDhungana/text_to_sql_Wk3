# Text-to-SQL Evaluation Framework Document

## Context
This document provides a comprehensive evaluation framework for a Text-to-SQL agent that converts natural language questions into PostgreSQL queries. The framework covers SQL correctness, execution metrics, result accuracy, system performance, robustness, and natural language quality dimensions.

## Document Structure
1. SQL Correctness Metrics
2. Execution Metrics
3. Result Accuracy Metrics
4. System Performance Metrics
5. Robustness Metrics
6. Natural Language Quality Metrics
7. Sample Evaluation Scorecard

---

## 1. SQL Correctness Metrics

### 1.1 Exact Match
**Definition:** String comparison of generated SQL vs. ground truth after normalization (whitespace, case, alias removal).

**Formula:**
```
Exact Match Score = (Number of exact matches) / (Total queries) × 100
```

**Good Score:** ≥ 85% for simple queries; ≥ 60% for complex multi-join queries.

**Measurement:**
- Normalize both SQL strings (lowercase, remove extra whitespace, standardize aliases)
- Compare character-by-character
- **Note:** This is a strict metric; semantically equivalent queries with different syntax will fail.

---

### 1.2 Execution Match
**Definition:** Generated SQL produces the same result set as ground truth, regardless of syntax differences.

**Formula:**
```
Execution Match Score = (Queries with matching result sets) / (Total queries) × 100
```

**Good Score:** ≥ 95% for simple queries; ≥ 80% for complex queries.

**Measurement:**
- Execute both generated and ground truth SQL
- Compare result sets (sorted comparison, since ORDER BY may differ)
- Handle floating point with epsilon tolerance (e.g., 1e-6)

```python
# Pseudocode

def execution_match(generated_sql, ground_truth_sql, epsilon=1e-6):
    try:
        gen_results = execute(generated_sql)
        gt_results = execute(ground_truth_sql)

        if len(gen_results) != len(gt_results):
            return False

        for gen_row, gt_row in zip(sorted(gen_results), sorted(gt_results)):
            for gen_val, gt_val in zip(gen_row, gt_row):
                if isinstance(gen_val, float):
                    if abs(gen_val - gt_val) > epsilon:
                        return False
                else:
                    if gen_val != gt_val:
                        return False
        return True
    except:
        return False
```

---

### 1.3 Component-Level Accuracy
**Definition:** Break down SQL into structural components and evaluate each independently.

#### 1.3.1 Table Selection Accuracy
**Formula:**
```
Table Accuracy = (Correct tables selected) / (Total required tables) × 100
```
**Good Score:** ≥ 95%

#### 1.3.2 Column Selection Accuracy
**Formula:**
```
Column Accuracy = (Correct columns in SELECT) / (Total required columns) × 100
```
**Good Score:** ≥ 90%

#### 1.3.3 JOIN Accuracy
**Formula:**
```
JOIN Accuracy = (Correct JOINs) / (Total required JOINs) × 100
```
**Good Score:** ≥ 85%

#### 1.3.4 WHERE Condition Accuracy
**Formula:**
```
WHERE Accuracy = (Correct conditions) / (Total required conditions) × 100
```
**Good Score:** ≥ 85%

#### 1.3.5 Aggregation Accuracy
**Formula:**
```
Aggregation Accuracy = (Correct aggregation functions) / (Total required aggregations) × 100
```
**Good Score:** ≥ 90%

**Implementation (Pseudocode):**
```python
import sqlparse

def parse_sql_components(sql):
    parsed = sqlparse.parse(sql)[0]
    components = {
        'tables': [],
        'columns': [],
        'joins': [],
        'where_conditions': [],
        'aggregations': []
    }

    for token in parsed.tokens:
        if isinstance(token, sqlparse.sql.Identifier):
            # Extract table/column names
            pass
        elif isinstance(token, sqlparse.sql.Where):
            # Extract WHERE conditions
            pass
        elif 'JOIN' in str(token):
            # Extract JOIN conditions
            pass
        elif any(agg in str(token) for agg in ['SUM', 'AVG', 'COUNT', 'MAX', 'MIN']):
            # Extract aggregation functions
            pass

    return components

def component_accuracy(generated_sql, ground_truth_sql):
    gen_components = parse_sql_components(generated_sql)
    gt_components = parse_sql_components(ground_truth_sql)

    results = {}
    for component in ['tables', 'columns', 'joins', 'where_conditions', 'aggregations']:
        gen_set = set(gen_components[component])
        gt_set = set(gt_components[component])

        correct = len(gen_set.intersection(gt_set))
        total = len(gt_set)

        results[component] = (correct / total * 100) if total > 0 else 100.0

    return results
```

---

## 2. Execution Metrics

### 2.1 Execution Success Rate
**Definition:** Percentage of generated queries that execute without error.

**Formula:**
```
Execution Success Rate = (Successful executions) / (Total queries) × 100
```

**Good Score:** ≥ 95%

**Measurement:**
```python
def measure_execution_success(queries, schema):
    total = len(queries)
    successful = 0
    error_types = {
        'syntax': 0,
        'table_not_found': 0,
        'column_not_found': 0,
        'logic_error': 0,
        'other': 0
    }

    for query in queries:
        try:
            execute(query)
            successful += 1
        except psycopg2.SyntaxError as e:
            error_types['syntax'] += 1
        except psycopg2.UndefinedTable as e:
            error_types['table_not_found'] += 1
        except psycopg2.UndefinedColumn as e:
            error_types['column_not_found'] += 1
        except Exception as e:
            if "logic" in str(e).lower():
                error_types['logic_error'] += 1
            else:
                error_types['other'] += 1

    success_rate = (successful / total) * 100
    return success_rate, error_types
```

### 2.2 Error Type Distribution
**Definition:** Categorize failures to identify systemic weaknesses.

| Error Category | Description | Target (< 5% each) |
|----------------|-------------|---------------------|
| Syntax Errors | Invalid SQL syntax | < 2% |
| Table Not Found | Referenced non-existent table | < 1% |
| Column Not Found | Referenced non-existent column | < 2% |
| Logic Errors | Wrong JOIN type, incorrect aggregation | < 3% |
| Permission Errors | Insufficient database permissions | < 1% |
| Timeout/Performance | Query exceeds time limit | < 2% |

### 2.3 Retry/Self-Correction Success Rate
**Definition:** Percentage of failed queries that succeed after self-correction.

**Formula:**
```
Self-Correction Rate = (Successful after retry) / (Failed initial attempts) × 100
```

**Good Score:** ≥ 70% for first retry; ≥ 90% cumulative after 2 retries.

**Measurement:**
```python
def measure_self_correction(agent, queries, max_retries=3):
    results = []

    for query in queries:
        attempts = 0
        success = False
        error_history = []

        while attempts < max_retries and not success:
            try:
                sql = agent.generate(query)
                execute(sql)
                success = True
            except Exception as e:
                error_history.append(str(e))
                agent.provide_feedback(str(e))  # Agent self-corrects
                attempts += 1

        results.append({
            'success': success,
            'attempts': attempts,
            'error_history': error_history
        })

    # Calculate metrics
    total_failed = sum(1 for r in results if r['attempts'] > 0)
    corrected = sum(1 for r in results if r['success'] and r['attempts'] > 0)

    self_correction_rate = (corrected / total_failed * 100) if total_failed > 0 else 100
    return self_correction_rate
```

---

## 3. Result Accuracy Metrics

### 3.1 Result Set Match
**Definition:** Compare generated SQL results with ground truth results.

#### Exact Match
**Formula:**
```
Exact Result Match = (Queries with identical result sets) / (Total queries) × 100
```

#### Partial Match (Fuzzy)
**Formula:**
```
Partial Match Score = (Common rows) / (Max(rows_in_gen, rows_in_gt)) × 100
```

**Good Score:**
- Exact match: ≥ 85%
- Partial match: ≥ 95%

**Implementation:**
```python
def result_match_score(gen_results, gt_results, match_type='exact'):
    if match_type == 'exact':
        if len(gen_results) != len(gt_results):
            return 0.0

        gen_set = set(tuple(row) for row in gen_results)
        gt_set = set(tuple(row) for row in gt_results)

        return 100.0 if gen_set == gt_set else 0.0

    elif match_type == 'partial':
        gen_set = set(tuple(row) for row in gen_results)
        gt_set = set(tuple(row) for row in gt_results)

        common = len(gen_set.intersection(gt_set))
        total = max(len(gen_set), len(gt_set))

        return (common / total * 100) if total > 0 else 100.0
```

### 3.2 Count Accuracy for Aggregation Queries
**Definition:** For COUNT/SUM/AVG queries, compare numeric results.

**Formula:**
```
Count Accuracy = 100 - |gen_value - gt_value| / gt_value × 100
```

**Good Score:** ≥ 99% (should be exact for counts)

### 3.3 Row Count Match for SELECT Queries
**Definition:** Compare number of rows returned.

**Formula:**
```
Row Count Match = 100 - |gen_row_count - gt_row_count| / max(gen_row_count, gt_row_count) × 100
```

**Good Score:** ≥ 95%

---

## 4. System Performance Metrics

### 4.1 Query Generation Latency
**Definition:** Time from receiving NL question to SQL generation completion.

**Formula:**
```
Average Generation Latency = SUM(generation_time) / Total queries (ms)
P95 Generation Latency = 95th percentile of generation times
P99 Generation Latency = 99th percentile of generation times
```

**Good Score:**
- Average: < 500ms
- P95: < 1000ms
- P99: < 2000ms

### 4.2 End-to-End Response Time
**Definition:** Total time from NL question to result return (including execution).

**Formula:**
```
Average E2E Time = SUM(total_response_time) / Total queries (ms)
```

**Good Score:**
- Average: < 2000ms
- P95: < 5000ms

### 4.3 Token Usage
**Definition:** Number of tokens consumed per query generation.

**Formula:**
```
Average Tokens = SUM(input_tokens + output_tokens) / Total queries
Cost per Query = Average Tokens × Price per token
```

**Good Score:**
- Average tokens: < 2000 tokens (for standard models)
- Cost efficiency: <$0.05 per query

**Measurement:**
```python
import time

def measure_performance(agent, queries):
    metrics = {
        'generation_latency': [],
        'e2e_time': [],
        'token_usage': []
    }

    for query in queries:
        start_time = time.time()

        # Generation
        gen_start = time.time()
        response = agent.generate(query)
        gen_end = time.time()

        # Execution
        execute(response['sql'])
        end_time = time.time()

        metrics['generation_latency'].append((gen_end - gen_start) * 1000)  # ms
        metrics['e2e_time'].append((end_time - start_time) * 1000)  # ms
        metrics['token_usage'].append(response['total_tokens'])

    return {
        'avg_generation_latency': sum(metrics['generation_latency']) / len(queries),
        'p95_generation_latency': percentile(metrics['generation_latency'], 95),
        'avg_e2e_time': sum(metrics['e2e_time']) / len(queries),
        'avg_token_usage': sum(metrics['token_usage']) / len(queries)
    }
```

---

## 5. Robustness Metrics

### 5.1 Ambiguity Handling
**Definition:** Accuracy on intentionally ambiguous questions.

**Test Categories:**
- Lexical ambiguity (same word, different meanings)
- Structural ambiguity (different parses)
- Context-dependent ambiguity (requires schema context)

**Formula:**
```
Ambiguity Score = (Appropriately handled ambiguous queries) / (Total ambiguous queries) × 100
```

**Good Score:** ≥ 80% (appropriately asks clarifying question or makes reasonable assumption)

### 5.2 No-Result Handling
**Definition:** Proper handling of queries that return zero rows.

**Formula:**
```
No-Result Score = (Correctly handled no-result queries) / (Total no-result queries) × 100
```

**Good Score:** ≥ 95% (returns empty set, not error; provides helpful message if NL answer expected)

### 5.3 Multi-Join Complex Query Handling
**Definition:** Accuracy on queries requiring 3+ table JOINs and/or nested subqueries.

**Formula:**
```
Complex Query Score = (Correct complex queries) / (Total complex queries) × 100
```

**Good Score:** ≥ 70%

**Complexity Scoring:**
```python
def query_complexity(sql):
    tables = count_tables(sql)
    joins = count_joins(sql)
    subqueries = count_subqueries(sql)
    aggregations = count_aggregations(sql)

    # Complexity score
    score = tables + (joins * 2) + (subqueries * 3) + (aggregations * 2)
    return score

# Complex if score >= 8
```

---

## 6. Natural Language Quality Metrics

### 6.1 Factual Accuracy
**Definition:** Does the NL answer correctly reflect the SQL results?

**Formula:**
```
Factual Accuracy = (Factually correct answers) / (Total answers) × 100
```

**Good Score:** ≥ 95%

### 6.2 Completeness
**Definition:** Does the answer include all relevant information from the result?

**Formula:**
```
Completeness = (Critical information included) / (Total critical information) × 100
```

**Good Score:** ≥ 90%

### 6.3 Readability (Automated)
**Definition:** Measure of text quality using standard NLP metrics.

**Metrics:**
- **Flesch Reading Ease:** Target: 60-70 (standard / easy to read)
- **Gunning Fog Index:** Target: < 12 (high school level)

**Formula:**
```python
def calculate_readability(text):
    # Using textstat library
    flesch = textstat.flesch_reading_ease(text)
    fog = textstat.gunning_fog(text)

    return {
        'flesch_reading_ease': flesch,
        'gunning_fog': fog
    }
```

**Good Score:**
- Flesch: ≥ 60
- Gunning Fog: ≤ 12

**NL Quality Evaluation Rubric:**

| Dimension | Excellent (5) | Good (4) | Fair (3) | Poor (2) | Fail (1) |
|-----------|---------------|----------|----------|----------|----------|
| Factual Accuracy | 100% accurate | Minor errors | Some misstatements | Major errors | Completely wrong |
| Completeness | All info present | Minor omission | Notable omission | Major omission | No useful info |
| Readability | Clear, fluent | Minor awkwardness | Some confusion | Hard to follow | Incoherent |

---

## 7. Sample Evaluation Scorecard

### 7.1 Overall Scorecard Template

| Metric | Weight | Score (0-100) | Weighted Score | Notes |
|--------|--------|---------------|----------------|-------|
| **SQL CORRECTNESS (30%)** |
| Exact Match | 10% | 82 | 8.2 |
| Execution Match | 10% | 94 | 9.4 |
| Component Accuracy | 10% | 88 | 8.8 |
| **EXECUTION (20%)** |
| Execution Success Rate | 10% | 97 | 9.7 |
| Self-Correction Rate | 10% | 85 | 8.5 |
| **RESULT ACCURACY (20%)** |
| Result Exact Match | 10% | 89 | 8.9 |
| Aggregation Accuracy | 10% | 96 | 9.6 |
| **PERFORMANCE (15%)** |
| Avg Generation Latency | 7.5% | 92 | 6.9 |
| Token Efficiency | 7.5% | 88 | 6.6 |
| **ROBUSTNESS (15%)** |
| Ambiguity Handling | 7.5% | 78 | 5.85 |
| Complex Query Handling | 7.5% | 72 | 5.4 |
| **NL QUALITY** (if applicable) |
| Factual Accuracy | 5% | 95 | 4.75 |
| Completeness | 3% | 90 | 2.7 |
| Readability | 2% | 88 | 1.76 |
| **TOTAL** | **100%** | | **84.9** |

### 7.2 Per-Query Detailed Report

| Query # | NL Question | Exact Match | Execution Match | Tables | Columns | JOINs | WHERE | Status | Time (ms) | Tokens |
|---------|-------------|-------------|-----------------|--------|---------|-------|-------|--------|-----------|--------|
| 1 | "List all products" | ✅ | ✅ | 1/1 | 0/0 | N/A | N/A | ✅ | 312 | 842 |
| 2 | "Get all customers" | ✅ | ✅ | 1/1 | 0/0 | N/A | N/A | ✅ | 298 | 765 |
| 3 | "Show all orders" | ✅ | ✅ | 1/1 | 0/0 | N/A | N/A | ✅ | 345 | 812 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| 21 | "Get orders with customer names" | ❌ | ✅ | 2/2 | 2/3 | 1/1 | N/A | ✅ | 520 | 1450 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| 31 | "Count customers per country" | ✅ | ✅ | 1/1 | 1/2 | N/A | N/A | ✅ | 410 | 920 |

### 7.3 Error Breakdown Report

| Error Type | Count | Percentage | Affected Queries |
|------------|-------|------------|------------------|
| Syntax Error | 2 | 4% | Q8, Q15 |
| Column Not Found | 1 | 2% | Q22 |
| Wrong JOIN Type | 3 | 6% | Q26, Q28, Q30 |
| Missing WHERE | 2 | 4% | Q35, Q38 |
| Wrong Aggregation | 1 | 2% | Q42 |

---

## Appendices

### Appendix A: Test Dataset Requirements
- Minimum 200 test queries
- Distribution: 20% simple (single table), 40% medium (1-2 JOINs), 40% complex (3+ JOINs, subqueries, aggregations)
- Coverage: All tables and relationships in schema
- Edge cases: Empty results, ambiguous queries, invalid schemas

### Appendix B: Automated Evaluation Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    EVALUATION PIPELINE                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Load Test Suite                                     │
│  - Load ground truth queries and expected results             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Generate SQL                                        │
│  - Feed NL question to Text-to-SQL agent                     │
│  - Capture generated SQL, latency, token usage               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Execute & Compare                                   │
│  - Run generated SQL against database                        │
│  - Compare results with ground truth                         │
│  - Record errors and classifications                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Calculate Metrics                                   │
│  - Compute all metrics per category                          │
│  - generate scorecard and reports                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: Report & Analyze                                    │
│  - Generate summary dashboard                                │
│  - Identify weakest areas for improvement                    │
└─────────────────────────────────────────────────────────────┘
```

### Appendix C: Implementation Code Stub

```python
# evaluation_framework.py

import time
import statistics
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

class ErrorType(Enum):
    SYNTAX = "syntax"
    TABLE_NOT_FOUND = "table_not_found"
    COLUMN_NOT_FOUND = "column_not_found"
    LOGIC_ERROR = "logic_error"
    OTHER = "other"

@dataclass
class EvaluationResult:
    query_id: str
    nl_question: str
    generated_sql: str
    ground_truth_sql: str
    exact_match: bool
    execution_match: bool
    execution_success: bool
    error_type: ErrorType = None
    generation_time_ms: float = 0.0
    token_count: int = 0

class TextToSQLEvaluator:
    def __init__(self, agent, schema, db_connection):
        self.agent = agent
        self.schema = schema
        self.db = db_connection
        self.results = []

    def evaluate(self, test_cases: List[Dict]) -> Dict:
        """Run full evaluation suite."""
        for case in test_cases:
            result = self._evaluate_single(case)
            self.results.append(result)

        return self._compute_metrics()

    def _evaluate_single(self, case: Dict) -> EvaluationResult:
        """Evaluate a single test case."""
        # Generate SQL
        start_time = time.time()
        response = self.agent.generate(case['question'])
        gen_time = (time.time() - start_time) * 1000

        # Check exact match
        exact_match = self._normalize(response['sql']) == self._normalize(case['ground_truth'])

        # Execute and compare
        execution_match = False
        execution_success = False
        error_type = None

        try:
            gen_results = self._execute(response['sql'])
            gt_results = self._execute(case['ground_truth'])
            execution_success = True
            execution_match = self._compare_results(gen_results, gt_results)
        except Exception as e:
            error_type = self._classify_error(str(e))

        return EvaluationResult(
            query_id=case['id'],
            nl_question=case['question'],
            generated_sql=response['sql'],
            ground_truth_sql=case['ground_truth'],
            exact_match=exact_match,
            execution_match=execution_match,
            execution_success=execution_success,
            error_type=error_type,
            generation_time_ms=gen_time,
            token_count=response.get('total_tokens', 0)
        )

    def _normalize(self, sql: str) -> str:
        """Normalize SQL for comparison."""
        import re
        sql = sql.lower().strip()
        sql = re.sub(r'\s+', ' ', sql)
        return sql

    def _execute(self, sql: str):
        """Execute SQL and return results."""
        with self.db.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def _compare_results(self, gen_results, gt_results, epsilon=1e-6) -> bool:
        """Compare two result sets."""
        if len(gen_results) != len(gt_results):
            return False

        gen_sorted = sorted(gen_results)
        gt_sorted = sorted(gt_results)

        for gen_row, gt_row in zip(gen_sorted, gt_sorted):
            for gen_val, gt_val in zip(gen_row, gt_row):
                if isinstance(gen_val, float):
                    if abs(gen_val - gt_val) > epsilon:
                        return False
                elif gen_val != gt_val:
                    return False

        return True

    def _classify_error(self, error_msg: str) -> ErrorType:
        """Classify error type from message."""
        if "syntax" in error_msg.lower():
            return ErrorType.SYNTAX
        elif "relation" in error_msg.lower() or "table" in error_msg.lower():
            return ErrorType.TABLE_NOT_FOUND
        elif "column" in error_msg.lower():
            return ErrorType.COLUMN_NOT_FOUND
        else:
            return ErrorType.OTHER

    def _compute_metrics(self) -> Dict:
        """Compute overall metrics from results."""
        total = len(self.results)

        exact_matches = sum(1 for r in self.results if r.exact_match)
        execution_matches = sum(1 for r in self.results if r.execution_match)
        execution_successes = sum(1 for r in self.results if r.execution_success)

        return {
            'exact_match_rate': exact_matches / total * 100,
            'execution_match_rate': execution_matches / total * 100,
            'execution_success_rate': execution_successes / total * 100,
            'average_latency': statistics.mean([r.generation_time_ms for r in self.results]),
            'p95_latency': statistics.quantiles([r.generation_time_ms for r in self.results], n=20)[18],
            'average_tokens': statistics.mean([r.token_count for r in self.results]),
            'error_breakdown': self._error_breakdown()
        }

    def _error_breakdown(self) -> Dict:
        """Breakdown of error types."""
        errors = {}
        for r in self.results:
            if r.error_type:
                errors[r.error_type.value] = errors.get(r.error_type.value, 0) + 1
        return errors

# Usage
# evaluator = TextToSQLEvaluator(agent, schema, db_connection)
# metrics = evaluator.evaluate(test_cases)
# print(metrics)
```
