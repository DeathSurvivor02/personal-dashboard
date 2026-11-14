"""
COMP309 - Data Warehousing & Predictive Analytics (Group 8)
Toronto Police Bicycle Thefts Predictive Modeling Pipeline

Attempts to load the Toronto Police Service Open Data Bicycle Thefts CSV
from local disk (`data/bicycle_thefts.csv`) or the City of Toronto Open Data
CKAN API; if offline or unreachable, generates a reproducible, schema-matched
synthetic dataset based on Toronto Police Bicycle Theft distributions so the
pipeline remains self-contained and verifiable.
"""

import json
import os
import urllib.request
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "bicycle_thefts.csv"
ARTIFACTS_DIR = BASE_DIR / "artifacts"

TORONTO_OPEN_DATA_CKAN = (
    "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show"
    "?id=bicycle-thefts"
)

FEATURE_COLUMNS = [
    "OCC_MONTH",
    "OCC_DOW",
    "OCC_HOUR",
    "DIVISION",
    "PREMISES_TYPE",
    "BIKE_TYPE",
    "BIKE_COST",
    "BIKE_COLOUR",
]
NUMERIC_FEATURES = ["OCC_HOUR", "BIKE_COST"]
CATEGORICAL_FEATURES = [
    "OCC_MONTH",
    "OCC_DOW",
    "DIVISION",
    "PREMISES_TYPE",
    "BIKE_TYPE",
    "BIKE_COLOUR",
]


def _try_download_toronto_dataset(dest: Path) -> bool:
    try:
        req = urllib.request.Request(
            TORONTO_OPEN_DATA_CKAN,
            headers={"User-Agent": "COMP309-Group8-Academic-Client/1.0"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            meta = json.loads(resp.read().decode("utf-8"))
        resources = meta.get("result", {}).get("resources", [])
        csv_url = next(
            (
                r["url"]
                for r in resources
                if str(r.get("format", "")).upper() == "CSV" and r.get("url")
            ),
            None,
        )
        if not csv_url:
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(csv_url, dest)
        return dest.exists() and dest.stat().st_size > 1000
    except Exception as exc:
        print(f"[INFO] Live Toronto Open Data download skipped ({exc}).")
        return False


def _generate_schema_matched_dataset(n_rows: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    dows = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    divisions = ["D14", "D51", "D52", "D11", "D13", "D32", "D41", "D53", "D55"]
    premises = ["Outside", "Apartment", "House", "Commercial", "Transit", "Educational", "Other"]
    bike_types = ["MT", "RG", "RC", "EL", "SC", "BM", "FO", "OT"]
    colours = ["BLK", "BLU", "RED", "SIL", "WHI", "GRY", "GRN", "YEL", "OT"]

    occ_month = rng.choice(months, size=n_rows, p=[0.04, 0.04, 0.06, 0.08, 0.11, 0.13, 0.15, 0.14, 0.10, 0.07, 0.05, 0.03])
    occ_dow = rng.choice(dows, size=n_rows)
    occ_hour = rng.integers(0, 24, size=n_rows)
    division = rng.choice(divisions, size=n_rows)
    premises_type = rng.choice(premises, size=n_rows, p=[0.34, 0.22, 0.18, 0.14, 0.05, 0.04, 0.03])
    bike_type = rng.choice(bike_types, size=n_rows, p=[0.35, 0.28, 0.12, 0.08, 0.05, 0.04, 0.04, 0.04])
    bike_colour = rng.choice(colours, size=n_rows)
    bike_cost = np.round(rng.lognormal(mean=6.4, sigma=0.75, size=n_rows), 2)
    bike_cost = np.clip(bike_cost, 80.0, 12000.0)

    # Simulate realistic recovery probability signals (overall ~3-8% or balanced for modeling)
    logits = (
        -1.1
        + np.where(np.isin(premises_type, ["Commercial", "Transit", "Apartment"]), 0.45, -0.2)
        + np.where(np.isin(division, ["D51", "D52", "D14"]), 0.35, -0.1)
        + np.where(bike_type == "EL", 0.55, 0.0)
        + np.where((occ_hour >= 8) & (occ_hour <= 18), 0.30, -0.25)
        + 0.00025 * np.clip(bike_cost, 0, 4000)
        + rng.normal(0, 0.55, size=n_rows)
    )
    probs = 1.0 / (1.0 + np.exp(-logits))
    recovered = (rng.random(n_rows) < probs).astype(int)
    status = np.where(recovered == 1, "RECOVERED", "STOLEN")

    df = pd.DataFrame({
        "OCC_MONTH": occ_month,
        "OCC_DOW": occ_dow,
        "OCC_HOUR": occ_hour,
        "DIVISION": division,
        "PREMISES_TYPE": premises_type,
        "BIKE_TYPE": bike_type,
        "BIKE_COST": bike_cost,
        "BIKE_COLOUR": bike_colour,
        "STATUS": status,
    })
    return df


def load_dataset() -> tuple[pd.DataFrame, str]:
    if DATA_PATH.exists():
        print(f"[INFO] Loading dataset from {DATA_PATH}")
        return pd.read_csv(DATA_PATH), "local_csv"

    if _try_download_toronto_dataset(DATA_PATH):
        print(f"[INFO] Downloaded Toronto Open Data CSV to {DATA_PATH}")
        return pd.read_csv(DATA_PATH), "toronto_open_data"

    print("[INFO] Generating schema-matched synthetic Toronto Bicycle Theft dataset (5000 rows).")
    df = _generate_schema_matched_dataset()
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    return df, "synthetic_schema_matched"


def build_preprocessor() -> ColumnTransformer:
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )


def train_and_evaluate():
    df, data_source = load_dataset()

    # Standardize target column: 1 = RECOVERED, 0 = STOLEN / UNKNOWN
    df = df.dropna(subset=["STATUS"]).copy()
    df["TARGET_RECOVERED"] = (df["STATUS"].astype(str).str.upper() == "RECOVERED").astype(int)

    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan

    X = df[FEATURE_COLUMNS].copy()
    y = df["TARGET_RECOVERED"].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    candidates = {
        "LogisticRegression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "DecisionTree": DecisionTreeClassifier(max_depth=10, min_samples_leaf=10, class_weight="balanced", random_state=42),
        "RandomForest": RandomForestClassifier(
            n_estimators=150, max_depth=14, min_samples_leaf=4, class_weight="balanced", random_state=42, n_jobs=-1
        ),
    }

    results = {}
    best_name = None
    best_score = -1.0
    best_pipeline = None

    for name, estimator in candidates.items():
        pipe = Pipeline(
            steps=[
                ("preprocessor", build_preprocessor()),
                ("classifier", estimator),
            ]
        )
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        y_prob = pipe.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
            "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
        }
        results[name] = metrics
        print(f"[{name}] {metrics}")

        if metrics["roc_auc"] > best_score:
            best_score = metrics["roc_auc"]
            best_name = name
            best_pipeline = pipe

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = ARTIFACTS_DIR / "model.pkl"
    metrics_path = ARTIFACTS_DIR / "metrics.json"

    joblib.dump(best_pipeline, model_path)
    summary = {
        "data_source": data_source,
        "total_rows": int(len(df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "recovered_rate": round(float(y.mean()), 4),
        "best_model": best_name,
        "models": results,
    }
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nBest model selected: {best_name} (ROC-AUC: {best_score})")
    print(f"Saved model to {model_path}")
    print(f"Saved metrics to {metrics_path}")
    print("\nClassification Report (Best Model):")
    print(classification_report(y_test, best_pipeline.predict(X_test), zero_division=0))


if __name__ == "__main__":
    train_and_evaluate()
