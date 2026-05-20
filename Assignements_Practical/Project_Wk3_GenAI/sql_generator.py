"""SQL generation from structured decomposition (Task 3) and NL-to-SQL (Task 4)."""
import re
from typing import Dict, Any, List
from database import SCHEMA, FK


def _quote(identifier: str) -> str:
    return f'"{identifier}"'


def _build_join(tables: List[str]) -> str:
    """Build JOIN clauses from table list based on FK relationships."""
    if len(tables) <= 1:
        return ""
    base = tables[0]
    join_clauses = []
    remaining = set(tables[1:])
    joined = {base}
    while remaining:
        found = False
        for table in list(remaining):
            for (from_table, from_col), (to_table, to_col) in FK.items():
                if from_table == table and to_table in joined:
                    alias_from = table[0] if table not in joined else table[0]
                    alias_to = to_table[0]
                    join_clauses.append(
                        f'JOIN {_quote(table)} ON {_quote(table)}.{_quote(from_col)} = {_quote(to_table)}.{_quote(to_col)}'
                    )
                    joined.add(table)
                    remaining.remove(table)
                    found = True
                    break
                elif to_table == table and from_table in joined:
                    join_clauses.append(
                        f'JOIN {_quote(table)} ON {_quote(from_table)}.{_quote(from_col)} = {_quote(table)}.{_quote(to_col)}'
                    )
                    joined.add(table)
                    remaining.remove(table)
                    found = True
                    break
            if found:
                break
        if not found:
            break
    return " ".join(join_clauses)


def generate_sql(decomposition: Dict[str, Any]) -> str:
    """Generate SQL from a structured decomposition dict."""
    tables = decomposition.get("Tables", [])
    columns = decomposition.get("Columns", [])
    filters = decomposition.get("Filters", "")
    joins = decomposition.get("Joins", "")
    aggregation = decomposition.get("Aggregation", "")
    sort_limit = decomposition.get("Sort/Limit", "")

    if not tables:
        raise ValueError("No tables specified in decomposition")

    main_table = tables[0]

    # Columns
    if columns == ["*"] or not columns:
        select_part = "*"
    else:
        processed_cols = []
        for col in columns:
            if " AS " in col.upper():
                processed_cols.append(col)
            elif "." in col and not col.startswith("("):
                processed_cols.append(col)
            else:
                processed_cols.append(col)
        select_part = ", ".join(processed_cols)

    query = f"SELECT {select_part} FROM {_quote(main_table)}"

    # Joins
    if joins:
        query += " " + joins
    elif len(tables) > 1:
        query += " " + _build_join(tables)

    # Filters (WHERE)
    if filters and filters != "None":
        query += f" WHERE {filters}"

    # Aggregation (GROUP BY / HAVING)
    if aggregation and aggregation != "None":
        query += " " + aggregation

    # Sort/Limit
    if sort_limit and sort_limit != "None":
        if not sort_limit.strip().upper().startswith("ORDER BY") and not sort_limit.strip().upper().startswith("LIMIT"):
            sort_limit = "ORDER BY " + sort_limit
        query += " " + sort_limit

    return query


def safe_sql_check(sql: str) -> bool:
    """Block dangerous SQL operations."""
    dangerous = ["DELETE", "DROP", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
    upper = sql.upper()
    for kw in dangerous:
        if kw in upper:
            return False
    if not upper.strip().startswith("SELECT"):
        return False
    return True


def read_sql_file(filepath: str = "sql_queries.sql") -> List[Dict[str, str]]:
    """Read the 50 benchmark queries and return list of {question, sql}."""
    import csv
    questions = []
    with open("SQL_BENCHMARK_QUESTIONS.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            questions.append(row['question'].strip() if 'question' in row else row.get(list(row.keys())[0], '').strip())

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    queries = {}
    current_q = None
    for line in lines:
        if line.strip().startswith("-- Q"):
            parts = line.strip().split(":")
            q_num = int(parts[0].replace("-- Q", "").strip())
            current_q = q_num
            queries[current_q] = {"question": questions[q_num - 1] if q_num <= len(questions) else "", "sql": ""}
        elif current_q and line.strip():
            queries[current_q]["sql"] += line.strip() + " "

    result = []
    for i in range(1, len(questions) + 1):
        if i in queries:
            result.append({
                "id": i,
                "question": queries[i]["question"],
                "sql": queries[i]["sql"].strip()
            })

    return result


def parse_decomposition(filepath: str = "SQL_BENCHMARK_QUESTIONS_DECOMPOSITION.md") -> List[Dict[str, Any]]:
    """Parse the decomposition markdown into structured dicts."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    decompositions = []
    sections = content.split("---")

    for section in sections:
        if not section.strip() or "Question " not in section:
            continue
        lines = section.strip().split("\n")
        dec = {}
        for line in lines:
            line = line.strip()
            if not line or line.startswith("## Question"):
                continue
            if line.startswith("-"):
                if ":" not in line:
                    continue
                # Remove leading "- "
                key_val = line.lstrip("- ").strip()
                key, val = key_val.split(":", 1)
                key = key.strip()
                val = val.strip()

                if key == "Tables":
                    if val == "*":
                        dec[key] = []
                    elif val == "None":
                        dec[key] = []
                    else:
                        dec[key] = [c.strip() for c in val.split(",")]
                elif key == "Columns":
                    if val == "*":
                        dec[key] = ["*"]
                    elif val == "None":
                        dec[key] = []
                    else:
                        parts = [c.strip() for c in val.split(",")]
                        dec[key] = parts
                elif key in ["Filters", "Joins", "Aggregation", "Sort/Limit", "Intent"]:
                    dec[key] = val
                else:
                    dec[key] = val

        if dec:
            decompositions.append(dec)

    return decompositions
