"""OpsTwin: single source of truth for paths, portfolio, services, ML and agent config."""
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent

@dataclass(frozen=True)
class Paths:
    root: Path = ROOT
    data: Path = ROOT / "data"
    bronze: Path = ROOT / "data" / "bronze"
    silver: Path = ROOT / "data" / "silver"
    gold: Path = ROOT / "data" / "gold"
    warehouse: Path = ROOT / "data" / "opstwin.duckdb"
    outputs: Path = ROOT / "outputs"
    logs: Path = ROOT / "outputs" / "logs"
    manifests: Path = ROOT / "outputs" / "manifests"

@dataclass(frozen=True)
class Portfolio:
    seed: int = 42
    sites: tuple = ("HYD-OLD-001", "GOA-VIL-002", "AMD-COW-003")
    start: str = "2025-01-01"
    months: int = 24
    sensors_per_site: int = 12
    assets_per_site: int = 8

@dataclass(frozen=True)
class Services:
    postgres_host: str = "localhost"
    postgres_port: int = 5433        # host 5433 -> container 5432, avoids local Postgres clash
    prefect_port: int = 4200
    api_port: int = 8000
    dashboard_port: int = 8501
    metabase_port: int = 3000
    proxy_port: int = 8080
    postgres_db: str = "opstwin_ops"
    postgres_user: str = "opstwin"
    postgres_password: str = "opstwin_local"

@dataclass(frozen=True)
class ML:
    test_size: float = 0.2
    random_state: int = 42
    forecast_horizon_days: int = 30

@dataclass(frozen=True)
class Agent:
    model: str = "gemini-3.5-flash"
    embedding_model: str = "text-embedding-004"
    offline_fallback: str = "ollama/llama3.2"
    max_sql_rows: int = 500

@dataclass(frozen=True)
class Sources:
    units_per_site: tuple = (15, 12, 40)          # rooms / rooms / desks
    base_adr: tuple = (8500, 7800, 1200)
    vendors: tuple = ("V-ALPHA", "V-BETA", "V-GAMMA", "V-DELTA")
    ticket_categories: tuple = ("HVAC", "Plumbing", "Electrical", "Lift", "Network", "Housekeeping")
    tickets_per_site_per_year: int = 200
    null_rate: float = 0.015
    duplicate_rate: float = 0.004
    outlier_rate: float = 0.002
    unit_drift_rate: float = 0.010                # temperature rows reported in Fahrenheit
    late_arrival_rate: float = 0.020


PATHS, PORTFOLIO, SERVICES, ML, AGENT = Paths(), Portfolio(), Services(), ML(), Agent()
SOURCES = Sources()

