"""Phase 6: deterministic eval harness - agent SQL vs ground-truth SQL."""
from __future__ import annotations

import json
from datetime import datetime, timezone

import duckdb

from config import PATHS
from src.agent.ask import ask

EVALS = [
    ("Which site generated the most total revenue?",
     "select site_id from marts.mart_site_daily_ops group by site_id order by sum(revenue_inr) desc limit 1"),
    ("How many maintenance tickets are still open?",
     "select count(*) from gold.fact_work_orders where status = 'OPEN'"),
    ("Which vendor has the highest SLA breach percentage?",
     "select vendor_id from marts.mart_vendor_performance order by breach_pct desc limit 1"),
    ("How many outlier sensor readings exist in total?",
     "select count(*) from gold.fact_telemetry where is_outlier"),
]


def main() -> None:
    con = duckdb.connect(str(PATHS.warehouse), read_only=True)
    results = []
    for question, truth_sql in EVALS:
        expected = con.execute(truth_sql).fetchall()
        out = ask(question)
        passed = out["status"] == "ok" and out["rows"] and str(out["rows"][0]) == str(expected[0])
        results.append({"question": question, "passed": passed,
                        "agent_sql": out.get("sql", ""), "expected_first_row": str(expected[0]),
                        "agent_first_row": str(out["rows"][0]) if out["rows"] else None})
        print(f"[eval] {'PASS' if passed else 'FAIL'} | {question}")
    con.close()

    accuracy = sum(r["passed"] for r in results) / len(results)
    payload = {"generated_at_utc": datetime.now(timezone.utc).isoformat(),
               "accuracy": accuracy, "results": results}
    PATHS.manifests.mkdir(parents=True, exist_ok=True)
    (PATHS.manifests / "phase6_agent_eval.json").write_text(json.dumps(payload, indent=2))
    print(f"[eval] accuracy = {accuracy:.0%} -> {PATHS.manifests / 'phase6_agent_eval.json'}")


if __name__ == "__main__":
    main()