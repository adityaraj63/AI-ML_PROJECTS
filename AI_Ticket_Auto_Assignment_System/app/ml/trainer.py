"""
ML Model Trainer
Trains Logistic Regression, Naive Bayes, and Linear SVM
Selects the best model based on F1 score and saves it with Joblib
"""
import os
import json
import time
import logging
import warnings
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from sklearn.calibration import CalibratedClassifierCV

from .preprocessor import preprocess_batch

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)


MODEL_DEFINITIONS = {
    "Logistic Regression": LogisticRegression(
        C=5.0,
        max_iter=1000,
        solver="lbfgs",
        multi_class="multinomial",
        class_weight="balanced",
        random_state=42,
    ),
    "Naive Bayes": MultinomialNB(alpha=0.1),
    "Linear SVM": CalibratedClassifierCV(
        LinearSVC(C=1.0, max_iter=2000, class_weight="balanced", random_state=42),
        cv=3,
    ),
}

TFIDF_PARAMS = {
    "max_features": 15000,
    "ngram_range": (1, 2),
    "sublinear_tf": True,
    "min_df": 2,
    "max_df": 0.95,
}


def build_pipeline(classifier) -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(**TFIDF_PARAMS)),
        ("clf", classifier),
    ])


def evaluate_model(pipeline: Pipeline, X_test: list, y_test: list) -> dict:
    """Compute all metrics for a trained pipeline."""
    y_pred = pipeline.predict(X_test)
    return {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "f1": round(f1_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, zero_division=0),
        "y_pred": y_pred.tolist(),
        "y_test": list(y_test),
    }


def plot_confusion_matrix(cm: list, labels: list, model_name: str, save_path: str):
    """Save a styled confusion matrix heatmap."""
    cm_arr = np.array(cm)
    fig, ax = plt.subplots(figsize=(12, 10))
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#1e293b")

    im = ax.imshow(cm_arr, cmap="Blues", aspect="auto")
    plt.colorbar(im, ax=ax)

    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9, color="white")
    ax.set_yticklabels(labels, fontsize=9, color="white")

    for i in range(len(labels)):
        for j in range(len(labels)):
            val = cm_arr[i, j]
            color = "white" if val < cm_arr.max() / 2 else "black"
            ax.text(j, i, str(val), ha="center", va="center", fontsize=7, color=color, fontweight="bold")

    ax.set_xlabel("Predicted Label", color="white", fontsize=12, labelpad=10)
    ax.set_ylabel("True Label", color="white", fontsize=12, labelpad=10)
    ax.set_title(f"Confusion Matrix — {model_name}", color="white", fontsize=14, fontweight="bold", pad=15)
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#334155")

    plt.tight_layout()
    plt.savefig(save_path, dpi=120, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


def plot_model_comparison(results: dict, save_path: str):
    """Bar chart comparing all models across metrics."""
    metrics = ["accuracy", "precision", "recall", "f1"]
    model_names = list(results.keys())
    x = np.arange(len(metrics))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#1e293b")

    colors = ["#6366f1", "#22c55e", "#f59e0b"]
    for i, (model_name, color) in enumerate(zip(model_names, colors)):
        vals = [results[model_name].get(m, 0) for m in metrics]
        bars = ax.bar(x + i * width, vals, width, label=model_name, color=color, alpha=0.85, edgecolor="#334155")
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.005,
                    f"{h:.3f}", ha="center", va="bottom", fontsize=8, color="white")

    ax.set_xticks(x + width)
    ax.set_xticklabels([m.title() for m in metrics], color="white", fontsize=11)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Score", color="white", fontsize=12)
    ax.set_title("Model Performance Comparison", color="white", fontsize=14, fontweight="bold")
    ax.tick_params(colors="white")
    ax.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="white", fontsize=10)
    for spine in ax.spines.values():
        spine.set_edgecolor("#334155")

    plt.tight_layout()
    plt.savefig(save_path, dpi=120, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


def train_and_save_best_model(dataset_path: str = None, model_dir: str = None) -> dict:
    """
    Full training pipeline:
    1. Load dataset
    2. Preprocess text
    3. Train all models
    4. Evaluate and select best
    5. Save best model + metadata
    6. Generate evaluation plots
    """
    # ── Paths ───────────────────────────────────────────────────────────────
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if dataset_path is None:
        dataset_path = os.path.join(base_dir, "dataset", "tickets.csv")
    if model_dir is None:
        model_dir = os.path.join(base_dir, "app", "ml", "saved_models")
    os.makedirs(model_dir, exist_ok=True)

    plots_dir = os.path.join(base_dir, "app", "static", "plots")
    os.makedirs(plots_dir, exist_ok=True)

    # ── Load data ───────────────────────────────────────────────────────────
    logger.info("Loading dataset from %s", dataset_path)
    df = pd.read_csv(dataset_path)
    logger.info("Dataset shape: %s", df.shape)

    # Combine title + description for richer features
    df["combined_text"] = df["title"].fillna("") + " " + df["description"].fillna("")

    # ── Preprocess ──────────────────────────────────────────────────────────
    logger.info("Preprocessing texts...")
    print("🔄 Preprocessing texts (this may take a few minutes)...")
    X_raw = df["combined_text"].tolist()
    y = df["department"].tolist()
    X_processed = preprocess_batch(X_raw, verbose=True)

    labels = sorted(list(set(y)))

    # ── Train/test split ────────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X_processed, y, test_size=0.2, random_state=42, stratify=y
    )
    logger.info("Train: %d, Test: %d", len(X_train), len(X_test))
    print(f"📊 Train: {len(X_train)}, Test: {len(X_test)}")

    # ── Train models ────────────────────────────────────────────────────────
    all_results = {}
    trained_pipelines = {}

    for model_name, clf in MODEL_DEFINITIONS.items():
        print(f"\n🤖 Training {model_name}...")
        start = time.time()
        pipeline = build_pipeline(clf)
        pipeline.fit(X_train, y_train)
        elapsed = time.time() - start

        metrics = evaluate_model(pipeline, X_test, y_test)
        metrics["training_time"] = round(elapsed, 2)
        all_results[model_name] = metrics
        trained_pipelines[model_name] = pipeline

        print(f"  ✓ Accuracy: {metrics['accuracy']:.4f} | F1: {metrics['f1']:.4f} | Time: {elapsed:.1f}s")
        logger.info(
            "%s — Accuracy: %.4f, F1: %.4f",
            model_name, metrics["accuracy"], metrics["f1"]
        )

        # Confusion matrix plot
        cm_path = os.path.join(plots_dir, f"cm_{model_name.lower().replace(' ', '_')}.png")
        plot_confusion_matrix(metrics["confusion_matrix"], labels, model_name, cm_path)

    # ── Select best model ───────────────────────────────────────────────────
    best_model_name = max(all_results, key=lambda m: all_results[m]["f1"])
    best_pipeline = trained_pipelines[best_model_name]
    best_metrics = all_results[best_model_name]
    print(f"\n🏆 Best Model: {best_model_name} (F1: {best_metrics['f1']:.4f})")

    # ── Comparison plot ─────────────────────────────────────────────────────
    comparison_path = os.path.join(plots_dir, "model_comparison.png")
    plot_model_comparison(
        {k: v for k, v in all_results.items() if k in MODEL_DEFINITIONS},
        comparison_path,
    )

    # ── Save best pipeline ──────────────────────────────────────────────────
    model_path = os.path.join(model_dir, "best_model.pkl")
    joblib.dump(best_pipeline, model_path)
    logger.info("Best model saved to %s", model_path)

    # ── Save metadata ───────────────────────────────────────────────────────
    metadata = {
        "best_model_name": best_model_name,
        "model_path": model_path,
        "labels": labels,
        "trained_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "dataset_size": len(df),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "metrics": {
            k: {mk: mv for mk, mv in v.items()
                if mk not in ("confusion_matrix", "classification_report", "y_pred", "y_test")}
            for k, v in all_results.items()
        },
        "best_metrics": {
            k: v for k, v in best_metrics.items()
            if k not in ("confusion_matrix", "y_pred", "y_test")
        },
        "tfidf_params": TFIDF_PARAMS,
    }

    meta_path = os.path.join(model_dir, "model_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Metadata saved to %s", meta_path)

    # ── Classification reports ──────────────────────────────────────────────
    for model_name, metrics in all_results.items():
        report_path = os.path.join(model_dir, f"report_{model_name.lower().replace(' ', '_')}.txt")
        with open(report_path, "w") as f:
            f.write(f"=== {model_name} ===\n\n")
            f.write(metrics["classification_report"])

    print(f"\n✅ Training complete! Model saved to: {model_path}")
    return metadata


if __name__ == "__main__":
    result = train_and_save_best_model()
    print(json.dumps({k: v for k, v in result.items() if k != "best_metrics"}, indent=2))
