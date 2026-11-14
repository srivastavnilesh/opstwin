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
    postgres_port: int = 5432
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
    model: str = "gemini-2.0-flash"
    embedding_model: str = "text-embedding-004"
    offline_fallback: str = "ollama/llama3.2"
    max_sql_rows: int = 500

PATHS, PORTFOLIO, SERVICES, ML, AGENT = Paths(), Portfolio(), Services(), ML(), Agent()