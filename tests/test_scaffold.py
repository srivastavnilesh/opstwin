"""Phase 0 invariants: interpreter pin, directory contract, core stack, platform tooling."""
import shutil
import sys

import config


def test_python_version():
    assert sys.version_info[:2] == (3, 12), "OpsTwin pins Python 3.12 for ML wheel compatibility"


def test_config_contract():
    assert config.PORTFOLIO.seed == 42
    assert len(config.PORTFOLIO.sites) == 3
    assert config.SERVICES.api_port == 8000
    assert config.AGENT.max_sql_rows == 500


def test_directory_contract():
    for d in ("src/data", "src/warehouse", "src/flows", "src/ml", "src/serving",
              "src/agent", "src/platform", "app", "tests", "docs", "scripts", "outputs/logs"):
        assert (config.ROOT / d).is_dir(), f"missing directory: {d}"

def test_core_imports():
    import importlib

    for name in ("duckdb", "fastapi", "mlflow", "pandas", "pandera", "prefect", "sklearn"):
        assert importlib.import_module(name) is not None, f"{name} not importable"


def test_platform_tooling():
    for tool in ("docker", "terraform", "kind", "kubectl"):
        assert shutil.which(tool), f"{tool} missing from PATH"