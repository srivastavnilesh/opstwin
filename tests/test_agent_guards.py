"""Phase 6: guardrail unit tests - no API key required."""
from src.agent.guards import apply_row_limit, validate_sql
from src.agent.schema_context import allowed_tables

TABLES = allowed_tables()


def test_valid_select_accepted():
    ok, msg = validate_sql("select site_id, sum(revenue_inr) from marts.mart_site_daily_ops group by 1", TABLES)
    assert ok and msg.startswith("select")


def test_cte_allowed():
    ok, _ = validate_sql("with t as (select site_id from marts.mart_site_daily_ops) select count(*) from t", TABLES)
    assert ok


def test_drop_refused():
    ok, _ = validate_sql("drop table marts.mart_site_daily_ops", TABLES)
    assert not ok


def test_unknown_table_refused():
    ok, msg = validate_sql("select * from secrets", TABLES)
    assert not ok and "allowlist" in msg


def test_multi_statement_refused():
    ok, _ = validate_sql("select 1; drop table x", TABLES)
    assert not ok


def test_row_limit_applied():
    assert "limit 500" in apply_row_limit("select 1", 500)