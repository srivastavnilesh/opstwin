"""Phase 1 invariants: determinism, partitioning, defect presence, source parity."""
import json

import pandas as pd
import pytest

import config
from src.data.generate import make_registry, make_telemetry

MANIFEST = config.PATHS.manifests / "phase1_bronze_manifest.json"


@pytest.fixture(scope="module")
def manifest():
    assert MANIFEST.exists(), "run the generator first"
    return json.loads(MANIFEST.read_text())


def test_manifest_contract(manifest):
    assert manifest["seed"] == config.PORTFOLIO.seed
    assert manifest["telemetry_partitions"] == len(config.PORTFOLIO.sites) * manifest["months"]
    assert manifest["row_counts"]["notes"] == manifest["row_counts"]["work_orders"]
    assert all(f["sha256"] and f["rows"] > 0 for f in manifest["files"])


def test_telemetry_determinism():
    a1, s1 = make_registry()
    a2, s2 = make_registry()
    t1 = make_telemetry(1, a1, s1)
    t2 = make_telemetry(1, a2, s2)
    assert pd.util.hash_pandas_object(t1, index=False).sum() == pd.util.hash_pandas_object(t2, index=False).sum()


def test_defects_present(manifest):
    parts = list(config.PATHS.bronze.glob("telemetry/site=*/month=*/part.csv"))
    df = pd.concat([pd.read_csv(p) for p in parts[:6]], ignore_index=True)
    assert df["value"].isna().sum() > 0, "null defect missing"
    assert df.duplicated().sum() > 0, "duplicate defect missing"
    assert (df["unit"] == "F").sum() > 0, "unit-drift defect missing"
    assert (df["ingested_at_utc"] > df["ts_utc"]).sum() > 0, "late arrivals missing"


def test_bronze_sources_exist(manifest):
    for rel in ("operational/bookings.csv", "operational/work_orders.csv",
                "vendor_sla/vendor_sla.csv", "maintenance_notes/notes.jsonl"):
        assert (config.PATHS.bronze / rel).exists(), rel


def test_postgres_roundtrip(manifest):
    assert manifest["postgres_used"] is True, "source-system extraction not exercised"


def test_calendar_window_exact():
    """--months N must span exactly N calendar months (no 30-day spill)."""
    from src.data.generate import _hours
    for n in (1, 2, 7, 24):
        ts = _hours(n)
        assert ts.tz_localize(None).to_period("M").nunique() == n, f"window spill at months={n}"