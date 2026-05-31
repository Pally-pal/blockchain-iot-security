"""
IoT Anomaly Detection — Model Training, Comparison & Selection Pipeline
=======================================================================
Dataset : Environmental Sensor Telemetry (Kaggle)
          https://www.kaggle.com/datasets/garystafford/environmental-sensor-data-132k
Author  : Oyelade Paul Oluwafemi  |  2021/37014

HOW TO USE WITH YOUR REAL DATA:
    Replace the `generate_synthetic_data()` call at the bottom with:
        df = pd.read_csv('iot_telemetry_data.csv')
    Then run:  python ml_pipeline.py
"""

import warnings
warnings.filterwarnings("ignore")

import os, time, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    accuracy_score, precision_score, recall_score, f1_score,
    roc_curve, auc
)
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier,
    IsolationForest, ExtraTreesClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier

OUT = "/home/claude/ml_output"
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# PALETTE
# ─────────────────────────────────────────────────────────────────────────────
NAVY   = "#0D1B2A"
BLUE   = "#1B4F72"
TEAL   = "#00A896"
MINT   = "#02C39A"
AMBER  = "#F4A300"
CORAL  = "#E74C3C"
SILVER = "#B0BEC5"
WHITE  = "#F0F4F8"

plt.rcParams.update({
    "figure.facecolor":  NAVY,
    "axes.facecolor":    "#07111A",
    "axes.edgecolor":    BLUE,
    "axes.labelcolor":   WHITE,
    "axes.titlecolor":   WHITE,
    "xtick.color":       SILVER,
    "ytick.color":       SILVER,
    "text.color":        WHITE,
    "grid.color":        BLUE,
    "grid.alpha":        0.4,
    "legend.facecolor":  NAVY,
    "legend.edgecolor":  BLUE,
    "font.family":       "DejaVu Sans",
})

# ─────────────────────────────────────────────────────────────────────────────
# 1.  SYNTHETIC DATA  (mirrors Kaggle CSV schema exactly)
# ─────────────────────────────────────────────────────────────────────────────
def generate_synthetic_data(n_normal=8000, n_anomaly=2000, seed=42):
    """
    Generates data that mirrors the Environmental Sensor Telemetry dataset.
    Columns: ts, device, co, humidity, light, lpg, motion, smoke, temp
    Label  : 0 = normal, 1 = anomaly (attack / sensor fault / injection)
    """
    rng = np.random.default_rng(seed)
    devices = ["b8:27:eb:bf:9d:51", "00:0f:00:70:91:0a", "b8:27:eb:64:65:05"]

    def normal_records(n):
        return pd.DataFrame({
            "ts":       rng.uniform(1.59e9, 1.60e9, n),
            "device":   rng.choice(devices, n),
            "co":       rng.uniform(0.003, 0.008, n),
            "humidity": rng.uniform(45, 70, n),
            "light":    rng.choice([True, False], n, p=[0.6, 0.4]),
            "lpg":      rng.uniform(0.007, 0.012, n),
            "motion":   rng.choice([True, False], n, p=[0.3, 0.7]),
            "smoke":    rng.uniform(0.012, 0.022, n),
            "temp":     rng.uniform(18, 28, n),
            "label":    0,
        })

    def anomaly_records(n):
        """
        Three attack/fault sub-types:
          A) Data injection    — extreme sensor values
          B) Sensor fault      — near-zero or NaN-like flat lines
          C) Replay attack     — repeated identical timestamps
        """
        n_a, n_b, n_c = n // 3, n // 3, n - 2*(n // 3)

        # A: injection
        inj = pd.DataFrame({
            "ts":       rng.uniform(1.59e9, 1.60e9, n_a),
            "device":   rng.choice(devices, n_a),
            "co":       rng.uniform(0.05, 0.3, n_a),      # very high CO
            "humidity": rng.uniform(0, 10, n_a),           # implausibly low
            "light":    rng.choice([True, False], n_a),
            "lpg":      rng.uniform(0.08, 0.5, n_a),       # very high LPG
            "motion":   rng.choice([True, False], n_a),
            "smoke":    rng.uniform(0.15, 0.8, n_a),       # very high smoke
            "temp":     rng.uniform(55, 90, n_a),           # impossible temp
            "label":    1,
        })
        # B: sensor fault
        fault = pd.DataFrame({
            "ts":       rng.uniform(1.59e9, 1.60e9, n_b),
            "device":   rng.choice(devices, n_b),
            "co":       rng.uniform(0.0, 0.0005, n_b),    # flat zero
            "humidity": rng.uniform(99, 100, n_b),          # pegged high
            "light":    False,
            "lpg":      rng.uniform(0.0, 0.0005, n_b),
            "motion":   False,
            "smoke":    rng.uniform(0.0, 0.0005, n_b),
            "temp":     rng.uniform(-5, 0, n_b),            # below zero
            "label":    1,
        })
        # C: replay (timestamp clustering)
        base_ts = rng.choice(rng.uniform(1.59e9, 1.60e9, 10), n_c)
        replay = pd.DataFrame({
            "ts":       base_ts + rng.uniform(-0.1, 0.1, n_c),
            "device":   rng.choice(devices[:1], n_c),       # same device
            "co":       rng.uniform(0.003, 0.008, n_c),
            "humidity": rng.uniform(45, 70, n_c),
            "light":    rng.choice([True, False], n_c),
            "lpg":      rng.uniform(0.007, 0.012, n_c),
            "motion":   rng.choice([True, False], n_c),
            "smoke":    rng.uniform(0.012, 0.022, n_c),
            "temp":     rng.uniform(18, 28, n_c),
            "label":    1,
        })
        return pd.concat([inj, fault, replay], ignore_index=True)

    df = pd.concat([normal_records(n_normal), anomaly_records(n_anomaly)], ignore_index=True)
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2.  PREPROCESSING
# ─────────────────────────────────────────────────────────────────────────────
def preprocess(df):
    print("\n[1/6] Preprocessing data...")
    df = df.copy()

    # Encode categoricals
    le_device = LabelEncoder()
    df["device_enc"] = le_device.fit_transform(df["device"])
    df["light"]  = df["light"].astype(int)
    df["motion"] = df["motion"].astype(int)

    # Feature engineering
    # Engineered features — must match ml_module.py _build_feature_row() exactly
    df["gas_index"]    = df["co"] + df["lpg"] + df["smoke"]
    df["co_lpg_ratio"] = df["co"] / (df["lpg"] + 1e-9)
    df["heat_index"]   = df["temp"] * (1 + 0.33 * df["humidity"] / 100)
    df["co_temp"]      = df["co"] * df["temp"]

    features = [
        "co", "humidity", "light", "lpg", "motion", "smoke", "temp",
        "device_enc", "gas_index", "co_lpg_ratio", "heat_index", "co_temp"
    ]

    X = df[features]
    y = df["label"]

    print(f"    Samples : {len(df):,}   |   Normal: {(y==0).sum():,}   Anomaly: {(y==1).sum():,}")
    print(f"    Features: {len(features)}  {features}")
    return X, y, features, le_device


# ─────────────────────────────────────────────────────────────────────────────
# 3.  MODELS
# ─────────────────────────────────────────────────────────────────────────────
def get_models():
    return {
        "Logistic Regression":     LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree":           DecisionTreeClassifier(max_depth=10, random_state=42),
        "K-Nearest Neighbours":    KNeighborsClassifier(n_neighbors=7),
        "Naïve Bayes":             GaussianNB(),
        "Support Vector Machine":  SVC(kernel="rbf", probability=True, random_state=42),
        "Random Forest":           RandomForestClassifier(n_estimators=150, random_state=42, n_jobs=-1),
        "Extra Trees":             ExtraTreesClassifier(n_estimators=150, random_state=42, n_jobs=-1),
        "Gradient Boosting":       GradientBoostingClassifier(n_estimators=150, random_state=42),
        "XGBoost":                 XGBClassifier(n_estimators=150, use_label_encoder=False,
                                                  eval_metric="logloss", random_state=42,
                                                  verbosity=0),
        "MLP Neural Network":      MLPClassifier(hidden_layer_sizes=(128, 64, 32),
                                                  max_iter=300, random_state=42),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4.  TRAIN & EVALUATE
# ─────────────────────────────────────────────────────────────────────────────
def train_and_evaluate(X, y):
    print("\n[2/6] Splitting data (80/20 stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    models = get_models()
    results = {}

    print(f"\n[3/6] Training {len(models)} models...\n")
    print(f"  {'Model':<28} {'Acc':>7} {'Prec':>7} {'Rec':>7} {'F1':>7} {'AUC':>7} {'Time':>8}")
    print("  " + "─" * 73)

    for name, model in models.items():
        t0 = time.time()
        model.fit(X_train_sc, y_train)
        train_time = time.time() - t0

        y_pred  = model.predict(X_test_sc)
        y_proba = model.predict_proba(X_test_sc)[:, 1] if hasattr(model, "predict_proba") else None

        acc   = accuracy_score(y_test, y_pred)
        prec  = precision_score(y_test, y_pred, zero_division=0)
        rec   = recall_score(y_test, y_pred, zero_division=0)
        f1    = f1_score(y_test, y_pred, zero_division=0)
        auc_s = roc_auc_score(y_test, y_proba) if y_proba is not None else 0.0
        cm    = confusion_matrix(y_test, y_pred)
        report = classification_report(y_test, y_pred, target_names=["Normal","Anomaly"], output_dict=True)

        # 5-fold CV F1
        cv_scores = cross_val_score(model, X_train_sc, y_train, cv=5, scoring="f1", n_jobs=-1)

        results[name] = {
            "model":       model,
            "acc":         acc,
            "precision":   prec,
            "recall":      rec,
            "f1":          f1,
            "auc":         auc_s,
            "cv_f1_mean":  cv_scores.mean(),
            "cv_f1_std":   cv_scores.std(),
            "train_time":  train_time,
            "cm":          cm,
            "y_pred":      y_pred,
            "y_proba":     y_proba,
            "report":      report,
        }

        print(f"  {name:<28} {acc:>7.4f} {prec:>7.4f} {rec:>7.4f} {f1:>7.4f} {auc_s:>7.4f} {train_time:>7.2f}s")

    return results, scaler, X_train_sc, X_test_sc, y_train, y_test


# ─────────────────────────────────────────────────────────────────────────────
# 5.  VISUALISATIONS
# ─────────────────────────────────────────────────────────────────────────────
def plot_all(results, y_test, X, features):
    names  = list(results.keys())
    short  = [n.replace("Gradient Boosting","Grad Boost").replace("K-Nearest Neighbours","KNN")
               .replace("Support Vector Machine","SVM").replace("Logistic Regression","Log Reg")
               .replace("MLP Neural Network","MLP").replace("Extra Trees","Extra Trees")
               .replace("Naïve Bayes","Naïve Bayes") for n in names]

    accs   = [results[n]["acc"]       for n in names]
    precs  = [results[n]["precision"] for n in names]
    recs   = [results[n]["recall"]    for n in names]
    f1s    = [results[n]["f1"]        for n in names]
    aucs   = [results[n]["auc"]       for n in names]
    times  = [results[n]["train_time"]for n in names]
    cv_f1  = [results[n]["cv_f1_mean"]for n in names]
    cv_std = [results[n]["cv_f1_std"] for n in names]

    # ── Fig 1: Grouped metric bar chart ──────────────────────────────────────
    fig, ax = plt.subplots(figsize=(16, 7), facecolor=NAVY)
    ax.set_facecolor("#07111A")
    x = np.arange(len(names))
    w = 0.18
    bars = [
        ax.bar(x - 2*w, accs,  w, label="Accuracy",  color=TEAL,  alpha=0.9),
        ax.bar(x -   w, precs, w, label="Precision", color=MINT,  alpha=0.9),
        ax.bar(x,       recs,  w, label="Recall",    color=AMBER, alpha=0.9),
        ax.bar(x +   w, f1s,   w, label="F1 Score",  color=CORAL, alpha=0.9),
        ax.bar(x + 2*w, aucs,  w, label="AUC-ROC",   color=SILVER,alpha=0.9),
    ]
    for bar_group in bars:
        for bar in bar_group:
            h = bar.get_height()
            if h > 0.01:
                ax.text(bar.get_x() + bar.get_width()/2, h + 0.005,
                        f"{h:.3f}", ha="center", va="bottom", fontsize=6.5, color=WHITE)
    ax.set_xticks(x)
    ax.set_xticklabels(short, rotation=30, ha="right", fontsize=10)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title("Model Performance Comparison — Accuracy / Precision / Recall / F1 / AUC", fontsize=13, pad=12)
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig1_model_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("    ✓ fig1_model_comparison.png")

    # ── Fig 2: Confusion matrices (2 rows × 5 cols) ──────────────────────────
    fig, axes = plt.subplots(2, 5, figsize=(22, 9), facecolor=NAVY)
    fig.suptitle("Confusion Matrices — All Models", fontsize=15, color=WHITE, y=1.01)
    for ax, name, sname in zip(axes.flat, names, short):
        cm = results[name]["cm"]
        sns.heatmap(cm, annot=True, fmt="d", ax=ax, cmap="YlOrRd",
                    linewidths=0.5, linecolor=NAVY,
                    xticklabels=["Normal","Anomaly"],
                    yticklabels=["Normal","Anomaly"],
                    cbar=False, annot_kws={"size": 13, "color": "white"})
        ax.set_title(sname, fontsize=11, color=TEAL)
        ax.set_xlabel("Predicted", fontsize=9)
        ax.set_ylabel("Actual", fontsize=9)
        ax.tick_params(colors=SILVER)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig2_confusion_matrices.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print("    ✓ fig2_confusion_matrices.png")

    # ── Fig 3: ROC curves ────────────────────────────────────────────────────
    colors = [TEAL, MINT, AMBER, CORAL, SILVER, "#6C63FF", "#FF6B6B", "#4ECDC4", "#FFD93D", "#C9CBFF"]
    fig, ax = plt.subplots(figsize=(10, 8), facecolor=NAVY)
    ax.set_facecolor("#07111A")
    for (name, res), color in zip(results.items(), colors):
        if res["y_proba"] is not None:
            fpr, tpr, _ = roc_curve(y_test, res["y_proba"])
            ax.plot(fpr, tpr, lw=2, color=color,
                    label=f"{name.replace('K-Nearest Neighbours','KNN').replace('Gradient Boosting','Grad Boost').replace('Support Vector Machine','SVM').replace('Logistic Regression','Log Reg').replace('MLP Neural Network','MLP')} (AUC={res['auc']:.4f})")
    ax.plot([0,1],[0,1],"--", color=BLUE, lw=1, label="Random Classifier (AUC=0.50)")
    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("ROC Curves — All Models", fontsize=13, pad=10)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig3_roc_curves.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("    ✓ fig3_roc_curves.png")

    # ── Fig 4: F1 with CV error bars ─────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(13, 6), facecolor=NAVY)
    ax.set_facecolor("#07111A")
    bar_colors = [CORAL if f == max(f1s) else TEAL for f in f1s]
    bars = ax.bar(short, f1s, color=bar_colors, alpha=0.85, zorder=3)
    ax.errorbar(short, cv_f1, yerr=cv_std, fmt="none", color=AMBER,
                capsize=5, capthick=2, elinewidth=2, zorder=4, label="5-Fold CV F1 ± std")
    ax.scatter(short, cv_f1, color=AMBER, s=50, zorder=5)
    for bar, val in zip(bars, f1s):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.012,
                f"{val:.4f}", ha="center", va="bottom", fontsize=9, color=WHITE)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("F1 Score", fontsize=12)
    ax.set_title("F1 Score per Model  +  5-Fold Cross Validation (Mean ± Std)", fontsize=13, pad=10)
    ax.set_xticklabels(short, rotation=30, ha="right", fontsize=10)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3, zorder=0)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig4_f1_cv.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("    ✓ fig4_f1_cv.png")

    # ── Fig 5: Training time ─────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(13, 5), facecolor=NAVY)
    ax.set_facecolor("#07111A")
    ax.barh(short[::-1], times[::-1], color=MINT, alpha=0.85)
    for i, (t, s) in enumerate(zip(times[::-1], short[::-1])):
        ax.text(t + 0.02, i, f"{t:.2f}s", va="center", fontsize=9, color=WHITE)
    ax.set_xlabel("Training Time (seconds)", fontsize=12)
    ax.set_title("Model Training Time Comparison", fontsize=13, pad=10)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig5_training_time.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("    ✓ fig5_training_time.png")

    # ── Fig 6: Radar / spider chart for top 5 ────────────────────────────────
    top5 = sorted(results.items(), key=lambda x: x[1]["f1"], reverse=True)[:5]
    metrics_labels = ["Accuracy", "Precision", "Recall", "F1", "AUC"]
    N = len(metrics_labels)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), facecolor=NAVY, subplot_kw=dict(polar=True))
    ax.set_facecolor("#07111A")
    spider_colors = [TEAL, MINT, AMBER, CORAL, SILVER]
    for (name, res), color in zip(top5, spider_colors):
        vals = [res["acc"], res["precision"], res["recall"], res["f1"], res["auc"]]
        vals += vals[:1]
        ax.plot(angles, vals, lw=2, color=color, label=name.replace("K-Nearest Neighbours","KNN")
                .replace("Gradient Boosting","Grad Boost").replace("Support Vector Machine","SVM")
                .replace("Logistic Regression","Log Reg").replace("MLP Neural Network","MLP"))
        ax.fill(angles, vals, alpha=0.1, color=color)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics_labels, fontsize=11, color=WHITE)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2","0.4","0.6","0.8","1.0"], color=SILVER, fontsize=8)
    ax.grid(color=BLUE, alpha=0.5)
    ax.tick_params(colors=SILVER)
    ax.set_title("Radar Chart — Top 5 Models", fontsize=13, color=WHITE, pad=18)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=10)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig6_radar_top5.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("    ✓ fig6_radar_top5.png")

    # ── Fig 7: Feature importance (best tree model) ──────────────────────────
    tree_models = ["XGBoost", "Random Forest", "Extra Trees", "Gradient Boosting", "Decision Tree"]
    for tm in tree_models:
        if tm in results and hasattr(results[tm]["model"], "feature_importances_"):
            importances = results[tm]["model"].feature_importances_
            fi_df = pd.DataFrame({"Feature": features, "Importance": importances})
            fi_df = fi_df.sort_values("Importance", ascending=True)

            fig, ax = plt.subplots(figsize=(10, 7), facecolor=NAVY)
            ax.set_facecolor("#07111A")
            colors_fi = [TEAL if i < len(fi_df)-3 else AMBER for i in range(len(fi_df))]
            bars = ax.barh(fi_df["Feature"], fi_df["Importance"], color=colors_fi, alpha=0.9)
            for bar, val in zip(bars, fi_df["Importance"]):
                ax.text(val + 0.002, bar.get_y() + bar.get_height()/2,
                        f"{val:.4f}", va="center", fontsize=9, color=WHITE)
            ax.set_xlabel("Feature Importance", fontsize=12)
            ax.set_title(f"Feature Importance — {tm}", fontsize=13, pad=10)
            ax.grid(axis="x", alpha=0.3)
            fig.tight_layout()
            fig.savefig(f"{OUT}/fig7_feature_importance.png", dpi=180, bbox_inches="tight")
            plt.close(fig)
            print(f"    ✓ fig7_feature_importance.png  ({tm})")
            break

    # ── Fig 8: Summary leaderboard ────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(14, 6), facecolor=NAVY)
    ax.set_facecolor(NAVY)
    ax.axis("off")

    ranked = sorted(results.items(), key=lambda x: (x[1]["f1"] + x[1]["auc"]) / 2, reverse=True)
    headers = ["Rank", "Model", "Accuracy", "Precision", "Recall", "F1 Score", "AUC-ROC", "CV F1", "Time(s)"]
    rows = []
    for i, (name, r) in enumerate(ranked):
        medal = ["🥇","🥈","🥉"] + [f" {j+1} " for j in range(3, len(ranked))]
        rows.append([
            medal[i], name,
            f"{r['acc']:.4f}", f"{r['precision']:.4f}",
            f"{r['recall']:.4f}", f"{r['f1']:.4f}",
            f"{r['auc']:.4f}", f"{r['cv_f1_mean']:.4f}±{r['cv_f1_std']:.4f}",
            f"{r['train_time']:.2f}s"
        ])

    col_widths = [0.045, 0.21, 0.085, 0.085, 0.075, 0.085, 0.085, 0.12, 0.08]
    x_positions = [sum(col_widths[:i]) + 0.02 for i in range(len(headers))]

    # Header row
    for j, (h, xp) in enumerate(zip(headers, x_positions)):
        ax.text(xp, 0.92, h, transform=ax.transAxes,
                fontsize=9, fontweight="bold", color=TEAL, va="top")

    ax.axhline(y=0.88, xmin=0.01, xmax=0.99, color=TEAL, linewidth=1)

    # Data rows
    for i, row in enumerate(rows):
        y = 0.82 - i * 0.073
        bg_color = "#112233" if i % 2 == 0 else "#0D1B2A"
        fancy = AMBER if i == 0 else (MINT if i == 1 else (SILVER if i == 2 else WHITE))
        for j, (cell, xp) in enumerate(zip(row, x_positions)):
            ax.text(xp, y, cell, transform=ax.transAxes,
                    fontsize=8.5, color=fancy if j < 2 else WHITE, va="top")

    ax.set_title("Model Leaderboard — Ranked by (F1 + AUC) / 2", fontsize=13,
                 color=WHITE, pad=12, loc="left", x=0.02)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig8_leaderboard.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("    ✓ fig8_leaderboard.png")


# ─────────────────────────────────────────────────────────────────────────────
# 6.  SELECT BEST & SAVE
# ─────────────────────────────────────────────────────────────────────────────
def select_and_save(results, scaler, features):
    print("\n[5/6] Selecting best model...")

    # Score = weighted combination
    scored = {
        name: 0.35*r["f1"] + 0.30*r["auc"] + 0.20*r["cv_f1_mean"] + 0.15*r["recall"]
        for name, r in results.items()
    }
    best_name = max(scored, key=scored.get)
    best = results[best_name]

    print(f"\n  ╔══════════════════════════════════════════════════════╗")
    print(f"  ║  🏆 BEST MODEL : {best_name:<35}║")
    print(f"  ║     Accuracy  : {best['acc']:.4f}                              ║")
    print(f"  ║     Precision : {best['precision']:.4f}                              ║")
    print(f"  ║     Recall    : {best['recall']:.4f}                              ║")
    print(f"  ║     F1 Score  : {best['f1']:.4f}                              ║")
    print(f"  ║     AUC-ROC   : {best['auc']:.4f}                              ║")
    print(f"  ║     CV F1     : {best['cv_f1_mean']:.4f} ± {best['cv_f1_std']:.4f}                     ║")
    print(f"  ╚══════════════════════════════════════════════════════╝")

    # ── Save bundle compatible with ml_module.py ──────────────────────────
    # ml_module.py loads a single dict with keys:
    #   model, scaler, feature_cols, model_name, metrics
    # metrics keys must be: 'Accuracy','Precision','Recall','F1 Score','ROC-AUC'
    bundle = {
        "model":        best["model"],
        "scaler":       scaler,
        "feature_cols": features,
        "model_name":   best_name,
        "metrics": {
            "Accuracy":  round(best["acc"],       4),
            "Precision": round(best["precision"], 4),
            "Recall":    round(best["recall"],    4),
            "F1 Score":  round(best["f1"],        4),
            "ROC-AUC":   round(best["auc"],       4),
        },
    }
    os.makedirs("ml_outputs", exist_ok=True)
    joblib.dump(bundle, "ml_outputs/best_iot_model.pkl")  # ← ml_module.py reads this
    joblib.dump(bundle, f"{OUT}/best_model.pkl")           # ← keep original path too

    meta = {
        "best_model_name":  best_name,
        "features":         features,
        "metrics": {
            "accuracy":    round(best["acc"],       4),
            "precision":   round(best["precision"], 4),
            "recall":      round(best["recall"],    4),
            "f1_score":    round(best["f1"],        4),
            "auc_roc":     round(best["auc"],       4),
            "cv_f1_mean":  round(best["cv_f1_mean"],4),
            "cv_f1_std":   round(best["cv_f1_std"], 4),
        },
        "all_models_ranked": [
            {
                "rank":      i+1,
                "name":      name,
                "f1":        round(results[name]["f1"],  4),
                "auc":       round(results[name]["auc"], 4),
                "accuracy":  round(results[name]["acc"], 4),
                "recall":    round(results[name]["recall"], 4),
                "precision": round(results[name]["precision"], 4),
                "cv_f1":     round(results[name]["cv_f1_mean"], 4),
                "train_time":round(results[name]["train_time"], 3),
            }
            for i, name in enumerate(sorted(scored, key=scored.get, reverse=True))
        ]
    }
    with open(f"{OUT}/model_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\n  Saved:")
    print(f"    {OUT}/best_model.pkl")
    print(f"    {OUT}/scaler.pkl")
    print(f"    {OUT}/model_metadata.json")
    return best_name, best


# ─────────────────────────────────────────────────────────────────────────────
# 7.  FLASK INTEGRATION SNIPPET (printed, not run)
# ─────────────────────────────────────────────────────────────────────────────
def print_flask_snippet(best_name, features):
    print(f"""
[6/6] Flask Integration Snippet
════════════════════════════════════════════════════════════════════

# Add this to your existing app.py  (top of file)
import joblib, numpy as np

ML_MODEL  = joblib.load("ml_output/best_model.pkl")   # {best_name}
ML_SCALER = joblib.load("ml_output/scaler.pkl")
ML_FEATURES = {features}

def ml_predict(sensor_data: dict) -> dict:
    \"\"\"Run anomaly detection on incoming IoT sensor data.\"\"\"
    try:
        row = np.array([[
            sensor_data.get("co", 0),
            sensor_data.get("humidity", 0),
            int(sensor_data.get("light", 0)),
            sensor_data.get("lpg", 0),
            int(sensor_data.get("motion", 0)),
            sensor_data.get("smoke", 0),
            sensor_data.get("temp", 0),
            sensor_data.get("device_enc", 0),
            sensor_data.get("co",0) + sensor_data.get("lpg",0) + sensor_data.get("smoke",0),
            sensor_data.get("co",0) / (sensor_data.get("lpg",1e-9) + 1e-9),
            sensor_data.get("temp",0) * (1 + 0.33 * sensor_data.get("humidity",0) / 100),
            sensor_data.get("co",0) * sensor_data.get("temp",0),
        ]])
        row_sc   = ML_SCALER.transform(row)
        pred     = int(ML_MODEL.predict(row_sc)[0])
        proba    = float(ML_MODEL.predict_proba(row_sc)[0][1])
        return {{
            "is_anomaly":    bool(pred),
            "anomaly_score": round(proba, 4),
            "risk_level":    "HIGH" if proba > 0.8 else "MEDIUM" if proba > 0.5 else "LOW",
            "model_used":    "{best_name}",
        }}
    except Exception as e:
        return {{"is_anomaly": False, "error": str(e)}}

# Inside your /api/register endpoint:
@app.route("/api/register", methods=["POST"])
def register_data():
    data = request.json
    ml_result = ml_predict(data.get("sensor_data", {{}}))   # ← ML CHECK
    data_hash = generate_hash(data)
    tx_hash   = blockchain_client.register_data(data_hash, data["device_id"])
    return jsonify({{
        "success":   True,
        "data_hash": data_hash,
        "tx_hash":   tx_hash,
        "ml_check":  ml_result,           # ← RETURNED IN RESPONSE
    }})

# New endpoint — standalone prediction
@app.route("/api/predict", methods=["POST"])
def predict():
    return jsonify(ml_predict(request.json.get("sensor_data", {{}})))

════════════════════════════════════════════════════════════════════
""")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 65)
    print("  IoT ANOMALY DETECTION — MODEL TRAINING & COMPARISON PIPELINE")
    print("=" * 65)

    # ── Load data ──
    # ✅ TO USE YOUR REAL KAGGLE DATA, replace these two lines:
    df = pd.read_csv('sensor_data.csv')
    df['label'] = 0   # then define anomalies based on your criteria
    print("\n[0/6] Loading real IoT sensor dataset...")
    # Flag anomalies based on physically implausible values
    df.loc[df['temp'] > 50, 'label'] = 1          # extreme temperature
    df.loc[df['co'] > 0.03, 'label'] = 1          # very high CO
    df.loc[df['smoke'] > 0.1, 'label'] = 1        # very high smoke
    df.loc[df['lpg'] > 0.06, 'label'] = 1         # very high LPG
    df.loc[df['humidity'] < 5, 'label'] = 1       # implausibly dry
    df.loc[df['temp'] < 0, 'label'] = 1           # below zero
    df.to_csv(f"{OUT}/synthetic_dataset.csv", index=False)
    print(f"    Dataset shape: {df.shape}")

    # ── Pipeline ──
    X, y, features, le_device = preprocess(df)
    results, scaler, X_train_sc, X_test_sc, y_train, y_test = train_and_evaluate(X, y)

    print("\n[4/6] Generating visualisations...")
    plot_all(results, y_test, X, features)

    best_name, best = select_and_save(results, scaler, features)
    print_flask_snippet(best_name, features)

    print("\n✅  Pipeline complete.")
    print(f"    All outputs saved to: {OUT}/")
    print(f"    Figures  : fig1–fig8 PNG files")
    print(f"    Model    : best_model.pkl  +  scaler.pkl")
    print(f"    Metadata : model_metadata.json\n")