"""Phase 3: Prefect orchestration for the OpsTwin pipeline.
Transforms manual commands into a resilient, scheduled, self-healing workflow.
"""
import subprocess
import sys
from pathlib import Path

from prefect import flow, get_run_logger, task

# Ensure repo root is on path for local execution
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

WAREHOUSE_DIR = ROOT / "src" / "warehouse"


def run_command(cmd: list[str], description: str) -> bool:
    """Helper to run shell commands and stream output to Prefect logs."""
    logger = get_run_logger()
    logger.info(f"Starting: {description}")
    logger.info(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd, 
            cwd=ROOT, 
            check=True, 
            capture_output=True, 
            text=True
        )
        # Stream stdout to Prefect UI/Logs
        for line in result.stdout.splitlines():
            logger.info(line)
        logger.info(f"Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"FAILED: {description}")
        logger.error(f"Return code: {e.returncode}")
        logger.error(f"STDOUT: {e.stdout}")
        logger.error(f"STDERR: {e.stderr}")
        raise RuntimeError(f"{description} failed")


@task(retries=2, retry_delay_seconds=10, name="Generate Bronze Data")
def generate_bronze(months: int = 24):
    """Run the seeded multi-source generator."""
    return run_command(
        [sys.executable, "-m", "src.data.generate", "--months", str(months)],
        "Seeded Data Generation"
    )


@task(retries=1, retry_delay_seconds=30, name="DBT Build (Silver/Gold)")
def run_dbt_build():
    """Run dbt build (seeds, models, tests) in the warehouse directory."""
    return run_command(
        [
            f"{ROOT}/.venv/bin/dbt", "build",
            "--project-dir", str(WAREHOUSE_DIR),
            "--profiles-dir", str(WAREHOUSE_DIR)
        ],
        "DBT Build"
    )


@task(retries=1, retry_delay_seconds=10, name="Profile & Reconcile")
def run_profiler():
    """Run the defect ledger profiler."""
    return run_command(
        [sys.executable, "-m", "src.warehouse.profile_warehouse"],
        "Warehouse Profiling"
    )


@task(name="Pipeline Success Notification")
def notify_success():
    logger = get_run_logger()
    logger.info("✅ OPS_TWIN PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("All stages executed. Data is ready for BI/ML consumption.")


@task(name="Pipeline Failure Notification")
def notify_failure():
    logger = get_run_logger()
    logger.error("❌ OPS_TWIN PIPELINE FAILED")
    logger.error("Check task logs for details. Alerting on-call engineer.")


@flow(
    name="opstwin_daily_pipeline",
    description="End-to-end orchestration: Bronze ingestion -> Silver/Gold transformation -> Profiling",
    retries=1,
    retry_delay_seconds=60
)
def main_pipeline(months: int = 24):
    logger = get_run_logger()
    logger.info(f"Starting OpsTwin Pipeline for {months} months of data")
    
    # 1. Ingestion
    gen_success = generate_bronze(months)
    
    # 2. Transformation (Depends on Gen)
    # wait_for ensures strict ordering. If gen fails, this never runs.
    dbt_success = run_dbt_build(wait_for=[gen_success])
    
    # 3. Profiling (Depends on DBT)
    profile_success = run_profiler(wait_for=[dbt_success])
    
    # 4. Notification
    if gen_success and dbt_success and profile_success:
        notify_success()
    else:
        notify_failure()


if __name__ == "__main__":
    # Run locally for development/testing
    main_pipeline(months=24)