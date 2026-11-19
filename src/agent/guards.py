"""Phase 6: SQL guardrails for the NL-to-SQL agent. Read-only by construction."""
from __future__ import annotations

import re

FORBIDDEN = (
    "insert", "update", "delete", "drop", "alter", "create", "attach", "detach",
    "copy", "pragma", "execute", "call", "merge", "truncate", "grant", "revoke",
    "export", "install", "load", "set", "vacuum",
)


def strip_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:sql)?\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    return t.strip()


def validate_sql(sql: str, allowed_tables: set[str]) -> tuple[bool, str]:
    s = strip_fences(sql).rstrip(";").strip()
    if not s:
        return False, "empty response"
    low = s.lower()
    if ";" in s:
        return False, "multiple statements are not allowed"
    if not (low.startswith("select") or low.startswith("with")):
        return False, "only SELECT or WITH statements are allowed"
    for kw in FORBIDDEN:
        if re.search(rf"\b{kw}\b", low):
            return False, f"forbidden keyword: {kw}"
    ctes = set(re.findall(r"\bwith\s+([a-z_][a-z0-9_]*)\s+as\s*\(", low))
    ctes |= set(re.findall(r",\s*([a-z_][a-z0-9_]*)\s+as\s*\(", low))
    refs = set(re.findall(r"\b(?:from|join)\s+([a-z_][a-z0-9_.]*)", low))
    unknown = refs - allowed_tables - ctes
    if unknown:
        return False, f"tables not in allowlist: {sorted(unknown)}"
    return True, s


def apply_row_limit(sql: str, limit: int) -> str:
    return f"select * from (\n{sql}\n) as _agent_limited limit {limit}"