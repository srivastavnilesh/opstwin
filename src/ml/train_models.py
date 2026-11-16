"""Phase 4: end-to-end ML lifecycle - clustering, risk prediction, MLflow tracking.

Two runs are logged per execution:
  1. sanity_synthetic_target - target derived from feature medians (validates plumbing)
  2. ground_truth_label      - target from staging.stg_assets health_state (real signal)
Comparing the two runs in MLflow is the leakage audit.
"""
from __future__ import annotations

from pathlib import Path

import duckdb
import mlflow
import mlflow.xgboost
import pandas as pd
import xgboost as xgb
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

from config import ML, PATHS

ROOT = Path(__file__).resolve().parents[2]

FEATURE_COLS = [
    "avg_vibration", "std_vibration", "avg_power",
    "outlier_count", "wo_count", "sla_breach_count",
]


def extract_features() -> pd.DataFrame:
    con = duckdb.connect(str(PATHS.warehouse), read_only=True)
    tel = con.execute("""
        select asset_id,
               count(*) as reading_count,
               avg(case when metric = 'vibration' then value_normalized end) as avg_vibration,
               max(case when metric = 'vibration' then value_normalized end) as max_vibration,
               stddev(case when metric = 'vibration' then value_normalized end) as std_vibration,
               avg(case when metric = 'power' then value_normalized end) as avg_power,
               sum(case when is_outlier then 1 else 0 end) as outlier_count
        from silver.silver_telemetry
        group by asset_id
    """).df()
    wo = con.execute("""
        select asset_id,
               count(*) as wo_count,
               sum(case when is_sla_breach then 1 else 0 end) as sla_breach_count,
               avg(resolution_hours) as avg_resolution_hours
        from silver.silver_work_orders
        group by asset_id
    """).df()
    labels = con.execute("select asset_id, health_state from staging.stg_assets").df()
    con.close()

    df = tel.merge(wo, on="asset_id", how="left").merge(labels, on="asset_id", how="left")
    df[FEATURE_COLS] = df[FEATURE_COLS].fillna(0)
    return df


def add_targets(df: pd.DataFrame) -> pd.DataFrame:
    med_out = df["outlier_count"].median()
    med_wo = df["wo_count"].median()
    df["target_sanity"] = ((df["outlier_count"] > med_out) | (df["wo_count"] > med_wo)).astype(int)
    df["target_label"] = (df["health_state"] == "degrading").astype(int)
    return df


def run_clustering(df: pd.DataFrame) -> pd.DataFrame:
    feats = ["avg_vibration", "std_vibration", "avg_power", "outlier_count", "wo_count"]
    scaled = StandardScaler().fit_transform(df[feats])
    km = KMeans(n_clusters=3, random_state=ML.random_state, n_init=10)
    df["health_cluster"] = km.fit_predict(scaled)
    order = df.groupby("health_cluster")["outlier_count"].mean().sort_values().index
    mapping = {order[0]: "Healthy", order[1]: "Degrading", order[2]: "Critical"}
    df["health_label"] = df["health_cluster"].map(mapping)
    return df


def train_and_log(df: pd.DataFrame, target_col: str, run_name: str) -> None:
    X = df[FEATURE_COLS]
    y = df[target_col]
    if y.sum() < 2 or (y == 0).sum() < 2:
        raise SystemExit(f"[ML] target '{target_col}' too imbalanced to train")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=ML.test_size, random_state=ML.random_state, stratify=y,
    )

    with mlflow.start_run(run_name=run_name):
        mlflow.log_params({
            "target": target_col, "test_size": ML.test_size,
            "n_estimators": 50, "max_depth": 4, "learning_rate": 0.1,
        })
        model = xgb.XGBClassifier(
            n_estimators=50, max_depth=4, learning_rate=0.1,
            random_state=ML.random_state, eval_metric="logloss",
        )
        model.fit(X_train, y_train)

        acc = accuracy_score(y_test, model.predict(X_test))
        auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
        cv = float("nan")
        if y.sum() >= 3 and (y == 0).sum() >= 3:
            cv = cross_val_score(model, X, y, cv=3, scoring="roc_auc").mean()

        mlflow.log_metrics({
            "accuracy": acc, "roc_auc": auc,
            "cv_roc_auc_mean": cv, "n_assets": len(df),
            "positives": int(y.sum()),
        })
        mlflow.xgboost.log_model(model, name="xgb_risk_model")

        print(f"   run={run_name}  acc={acc:.4f}  auc={auc:.4f}  cv_auc={cv:.4f}  positives={int(y.sum())}")


def main() -> None:
    mlflow.set_tracking_uri(f"sqlite:///{ROOT}/mlflow.db")
    mlflow.set_experiment("opstwin_asset_risk_prediction")

    print("[ML] Extracting features from DuckDB warehouse...")
    df = add_targets(run_clustering(extract_features()))
    print(f"[ML] {len(df)} assets | degrading={int(df.target_label.sum())} | sanity_pos={int(df.target_sanity.sum())}")
    print(df[["asset_id", "health_label", "outlier_count", "wo_count",
              "target_sanity", "target_label"]].head().to_string(index=False))

    print("[ML] Run 1/2 - sanity target (expect ~1.0, proves plumbing)...")
    train_and_log(df, "target_sanity", "sanity_synthetic_target")
    print("[ML] Run 2/2 - ground-truth degradation label (real signal)...")
    train_and_log(df, "target_label", "ground_truth_label")
    print("[ML] Phase 4 ML pipeline completed successfully.")


if __name__ == "__main__":
    main()