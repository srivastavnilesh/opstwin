"""Phase 6: guarded NL-to-SQL agent ('Ask the Twin')."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import duckdb
from dotenv import load_dotenv

from config import AGENT, PATHS
from src.agent.guards import apply_row_limit, strip_fences, validate_sql
from src.agent.schema_context import allowed_tables, build_schema_context

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

SYSTEM_PROMPT = """You are OpsTwin, an analyst agent over a DuckDB warehouse.
Rules:
- Return ONLY one DuckDB SQL SELECT statement. No prose, no markdown fences.
- Use only the tables and columns provided in SCHEMA.
- Aggregate precisely to answer the question.
"""


def _client():
    from google import genai
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY missing in .env - add your free AI Studio key")
    return genai.Client(api_key=key)


def _generate(client, prompt: str) -> str:
    resp = client.models.generate_content(model=AGENT.model, contents=prompt)
    return resp.text or ""


def ask(question: str) -> dict:
    tables = allowed_tables()
    context = build_schema_context(str(PATHS.warehouse), tables)
    client = _client()
    prompt = f"{SYSTEM_PROMPT}\n\nSCHEMA:\n{context}\n\nQUESTION:\n{question}\n\nSQL:"

    sql = strip_fences(_generate(client, prompt))
    ok, safe_sql = validate_sql(sql, tables)
    if not ok:
        return {"question": question, "status": "refused", "reason": safe_sql,
                "sql": sql, "rows": [], "narrative": ""}

    con = duckdb.connect(str(PATHS.warehouse), read_only=True)
    try:
        rows = con.execute(apply_row_limit(safe_sql, AGENT.max_sql_rows)).fetchall()
    except Exception as exc:
        repair = _generate(client, f"{prompt}\n\nYour previous SQL failed with:\n{exc}\n\nReturn corrected SQL only:")
        sql = strip_fences(repair)
        ok, safe_sql = validate_sql(sql, tables)
        if not ok:
            con.close()
            return {"question": question, "status": "refused", "reason": safe_sql, "sql": sql, "rows": [], "narrative": ""}
        rows = con.execute(apply_row_limit(safe_sql, AGENT.max_sql_rows)).fetchall()
    finally:
        con.close()

    narrative = _generate(
        client,
        f"Question: {question}\nResult rows (max 20): {rows[:20]}\n"
        "Answer in two plain-English sentences for a non-technical founder.",
    )
    return {"question": question, "status": "ok", "sql": safe_sql, "rows": rows[:20], "narrative": narrative}

def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit('usage: python -m src.agent.ask "your question"')
    print(json.dumps(ask(" ".join(sys.argv[1:])), indent=2, default=str))


if __name__ == "__main__":
    main()