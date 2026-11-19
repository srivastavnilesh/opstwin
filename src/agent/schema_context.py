"""Phase 6: dynamic schema context + business glossary for the agent prompt."""
from __future__ import annotations

import duckdb

GLOSSARY = {
    "marts.mart_site_daily_ops": "Daily site operations: occupancy_pct, revenue_inr, energy_kwh, water_litres, tickets_opened.",
    "marts.mart_asset_health_monthly": "Monthly asset health: avg/max vibration, power, outliers, tickets, mttr_hours, maintenance cost.",
    "marts.mart_vendor_performance": "Vendor scorecard: tickets, avg resolution hours, breach_pct, spend.",
    "gold.fact_telemetry": "Hourly sensor readings; metric in (temperature,humidity,power,water,vibration); is_outlier flag.",
    "gold.fact_work_orders": "Maintenance tickets; status OPEN/CLOSED; is_sla_breach; resolution_hours.",
    "gold.fact_bookings": "Unit-day bookings; is_occupied; revenue_inr; channel.",
    "gold.dim_site": "Sites: site_id like HYD-OLD-001; city; asset_class.",
    "gold.dim_date": "Calendar: date_key YYYYMMDD, month_start, is_weekend.",
}


def allowed_tables() -> set[str]:
    return {
        "marts.mart_site_daily_ops", "marts.mart_asset_health_monthly",
        "marts.mart_vendor_performance",
        "gold.dim_site", "gold.dim_asset", "gold.dim_sensor", "gold.dim_vendor", "gold.dim_date",
        "gold.fact_telemetry", "gold.fact_bookings", "gold.fact_work_orders",
        "gold.fact_vendor_sla_monthly",
    }


def build_schema_context(db_path: str, allowed: set[str]) -> str:
    con = duckdb.connect(db_path, read_only=True)
    rows = con.execute(
        "select table_schema, table_name, column_name, data_type "
        "from information_schema.columns "
        "where table_schema in ('marts', 'gold') order by 1, 2, ordinal_position"
    ).fetchall()
    con.close()
    tables: dict[str, list[str]] = {}
    for schema, table, col, dtype in rows:
        full = f"{schema}.{table}"
        if full in allowed:
            tables.setdefault(full, []).append(f"{col} ({dtype})")
    blocks = []
    for full, cols in tables.items():
        blocks.append(f"TABLE {full}\n  {GLOSSARY.get(full, '')}\n  columns: " + ", ".join(cols))
    return "\n\n".join(blocks)