"""Phase 2A: profile bronze vs silver and emit a defect ledger with reconciliation."""
"""Phase 2A: profile bronze vs silver and emit a defect ledger with reconciliation."""
from __future__ import annotations

import json
from datetime import datetime, timezone

import duckdb

from config import PATHS, SOURCES

def scalar(con, sql: str):
    return con.execute(sql).fetchone()[0]


def main() -> None:
    con = duckdb.connect(str(PATHS.warehouse), read_only=True)
    q = lambda sql: scalar(con, sql)  # noqa: E731

    bronze = q("select count(*) from staging.stg_telemetry")
    deduped = q("select count(*) from silver.int_telemetry_clean")
    silver = q("select count(*) from silver.silver_telemetry")
    quarantined = q("select count(*) from silver.silver_telemetry_quarantine")

    ledger = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "row_reconciliation": {
            "bronze_rows": bronze,
            "duplicates_removed": bronze - deduped,
            "deduped_rows": deduped,
            "quarantined_rows": quarantined,
            "silver_rows": silver,
            "balances": deduped == silver + quarantined,
        },
        "defects": {
            "nulls": {
                "expected_rate": SOURCES.null_rate,
                "observed_bronze": q("select count(*) from staging.stg_telemetry where value_raw is null"),
                "remaining_silver": q("select count(*) from silver.silver_telemetry where value_normalized is null"),
            },
            "duplicates": {
                "expected_rate": SOURCES.duplicate_rate,
                "removed": bronze - deduped,
                "remaining_silver": silver - q("select count(distinct reading_id) from silver.silver_telemetry"),
            },
            "unit_drift": {
                "expected_rate": SOURCES.unit_drift_rate,
                "observed_bronze_f": q("select count(*) from staging.stg_telemetry where unit_raw = 'F'"),
                "remaining_silver_f": q("select count(*) from silver.silver_telemetry where unit_normalized = 'F'"),
            },
            "late_arrivals": {
                "expected_rate": SOURCES.late_arrival_rate,
                "observed_bronze": q("select count(*) from staging.stg_telemetry where ingested_at_utc > ts_utc"),
                "flagged_silver": q("select count(*) from silver.silver_telemetry where is_late_arrival"),
            },
            "outliers": {
                "expected_rate": SOURCES.outlier_rate,
                "flagged_silver": q("select count(*) from silver.silver_telemetry where is_outlier"),
                "policy": "flagged, retained for failure analysis",
            },
        },
        "other_sources": {
            "bookings": q("select count(*) from silver.silver_bookings"),
            "work_orders": q("select count(*) from silver.silver_work_orders"),
            "sla_breaches": q("select count(*) from silver.silver_work_orders where is_sla_breach"),
            "notes": q("select count(*) from staging.stg_notes"),
            "vendor_sla": q("select count(*) from staging.stg_vendors_sla"),
        },
        "silver_metric_ranges": [
            dict(zip(["metric", "n", "min", "avg", "max"], row))
            for row in con.execute(
                "select metric, count(*), round(min(value_normalized),2), "
                "round(avg(value_normalized),2), round(max(value_normalized),2) "
                "from silver.silver_telemetry group by metric order by metric"
            ).fetchall()
        ],
    }
    con.close()

    PATHS.manifests.mkdir(parents=True, exist_ok=True)
    (PATHS.manifests / "phase2_profile.json").write_text(json.dumps(ledger, indent=2, default=str))
    reports = PATHS.outputs / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    r = ledger["row_reconciliation"]
    lines = [
        "# OpsTwin Phase 2A - Bronze to Silver Defect Ledger", "",
        f"Generated: {ledger['generated_at_utc']}", "",
        "## Row reconciliation", "",
        "| Stage | Rows |", "|---|---|",
        f"| Bronze | {r['bronze_rows']:,} |",
        f"| Duplicates removed | {r['duplicates_removed']:,} |",
        f"| Deduped | {r['deduped_rows']:,} |",
        f"| Quarantined (null) | {r['quarantined_rows']:,} |",
        f"| Silver (clean) | {r['silver_rows']:,} |",
        f"| Balances | {r['balances']} |", "",
        "## Defect resolution", "",
        "| Defect | Expected rate | Observed in bronze | Remaining in silver |",
        "|---|---|---|---|",
    ]
    d = ledger["defects"]
    lines += [
        f"| Nulls | {d['nulls']['expected_rate']:.3%} | {d['nulls']['observed_bronze']:,} | {d['nulls']['remaining_silver']} |",
        f"| Duplicates | {d['duplicates']['expected_rate']:.3%} | {d['duplicates']['removed']:,} | {d['duplicates']['remaining_silver']} |",
        f"| Unit drift (F) | {d['unit_drift']['expected_rate']:.3%} | {d['unit_drift']['observed_bronze_f']:,} | {d['unit_drift']['remaining_silver_f']} |",
        f"| Late arrivals | {d['late_arrivals']['expected_rate']:.3%} | {d['late_arrivals']['observed_bronze']:,} | flagged: {d['late_arrivals']['flagged_silver']:,} |",
        f"| Outliers | {d['outliers']['expected_rate']:.3%} | n/a | flagged: {d['outliers']['flagged_silver']:,} |",
        "", "## Silver metric ranges", "",
        "| Metric | Rows | Min | Avg | Max |", "|---|---|---|---|---|",
    ]
    for m in ledger["silver_metric_ranges"]:
        lines.append(f"| {m['metric']} | {m['n']:,} | {m['min']} | {m['avg']} | {m['max']} |")
    (reports / "phase2_profile.md").write_text("\n".join(lines) + "\n")

    print(json.dumps(ledger["row_reconciliation"], indent=2))
    print(f"[profile] ledger -> {PATHS.manifests / 'phase2_profile.json'}")
    print(f"[profile] report -> {reports / 'phase2_profile.md'}")
    if not r["balances"]:
        raise SystemExit("RECONCILIATION FAILED")


if __name__ == "__main__":
    main()