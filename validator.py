"""SQL validation and error classification."""
import re
import time
from typing import Dict, Any, List
from enum import Enum
from dataclasses import dataclass

class ErrorType(Enum):
    SYNTAX = "syntax"
    TABLE_NOT_FOUND = "table_not_found"
    COLUMN_NOT_FOUND = "column_not_found"
    PERMISSION = "permission"
    TIMEOUT = "timeout"
    LOGIC_ERROR = "logic_error"
    OTHER = "other"
    NONE = "none"


@dataclass
class ValidationResult:
    valid: bool
    error_type: ErrorType
    error_message: str
    suggestions: List[str]


def classify_error(error_msg: str) -> ErrorType:
    """Classify error type from error message."""
    msg = error_msg.lower()
    if "syntax" in msg or "error in sql statement" in msg:
        return ErrorType.SYNTAX
    elif "relation" in msg or "table" in msg:
        return ErrorType.TABLE_NOT_FOUND
    elif "column" in msg:
        return ErrorType.COLUMN_NOT_FOUND
    elif "permission" in msg:
        return ErrorType.PERMISSION
    elif "timeout" in msg or "canceling statement" in msg:
        return ErrorType.TIMEOUT
    elif "logic" in msg or "ambiguous" in msg:
        return ErrorType.LOGIC_ERROR
    else:
        return ErrorType.OTHER


def suggest_fix(error_type: ErrorType, sql: str, error_msg: str) -> List[str]:
    """Suggest fixes based on error type."""
    suggestions = []
    if error_type == ErrorType.SYNTAX:
        suggestions.append("Check for missing commas or parentheses")
        suggestions.append("Verify table/column names are properly quoted")
    elif error_type == ErrorType.TABLE_NOT_FOUND:
        suggestions.append("Check table name spelling and case")
        suggestions.append("Verify table exists in schema")
    elif error_type == ErrorType.COLUMN_NOT_FOUND:
        suggestions.append("Check column name spelling and case")
        suggestions.append("Verify column exists in the specified table")
    elif error_type == ErrorType.PERMISSION:
        suggestions.append("Check database permissions")
    return suggestions


def validate_query(sql: str) -> ValidationResult:
    """Validate a SQL query for safety and correctness before execution."""
    if not sql or not sql.strip():
        return ValidationResult(
            valid=False,
            error_type=ErrorType.SYNTAX,
            error_message="Empty SQL query",
            suggestions=["Provide a non-empty SQL query"]
        )

    upper = sql.upper()
    dangerous = ["DELETE", "DROP", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
    for kw in dangerous:
        if kw in upper:
            return ValidationResult(
                valid=False,
                error_type=ErrorType.PERMISSION,
                error_message=f"Dangerous operation detected: {kw}",
                suggestions=["Only SELECT queries are allowed"]
            )

    if not upper.strip().startswith("SELECT"):
        return ValidationResult(
            valid=False,
            error_type=ErrorType.SYNTAX,
            error_message="Query must start with SELECT",
            suggestions=["Rewrite query to start with SELECT"]
        )

    return ValidationResult(
        valid=True,
        error_type=ErrorType.NONE,
        error_message="",
        suggestions=[]
    )
