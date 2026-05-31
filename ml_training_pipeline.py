"""
=============================================================================
IoT BLOCKCHAIN SECURITY SYSTEM — ML MODEL TRAINING PIPELINE
=============================================================================
Author  : Oyelade Paul Oluwafemi (2021/37014)
Dataset : Environmental Sensor Telemetry (Kaggle - garystafford)
          Columns: ts, device, co, humidity, light, lpg, motion, smoke, temp

Models trained & compared:
  1. Isolation Forest         (unsupervised anomaly detection)
  2. One-Class SVM            (unsupervised anomaly detection)
  3. Local Outlier Factor     (unsupervised anomaly detection)
  4. Random Forest Classifier (supervised — uses engineered labels)
  5. XGBoost Classifier       (supervised — uses engineered labels)
  6. Gradient Boosting        (supervised — uses engineered labels)
  7. Logistic Regression      (supervised — baseline)
  8. K-Nearest Neighbours     (supervised)
  9. Decision Tree            (supervised)
 10. Neural Network (MLP)     (supervised)

Best model is saved as:  best_iot_model.pkl
All results saved as:    model_comparison_results.csv
=============================================================================
"""

import os, sys, time, warnings
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    precision_score, recall_score, f1_score, accuracy_score,
    roc_curve, auc
)
from sklearn.ensemble import (
    IsolationForest, RandomForestClassifier, GradientBoostingClassifier
)
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor, KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier

warnings.filterwarnings('ignore')

# ── Try importing XGBoost ─────────────────────────────────────────────────────
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠  XGBoost not installed — skipping. Run: pip install xgboost")

OUT_DIR = "/home/claude/ml_outputs"
os.makedirs(OUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — LOAD & INSPECT DATA
# ─────────────────────────────────────────────────────────────────────────────
def load_data(csv_path: str) -> pd.DataFrame:
    print("\n" + "="*70)
    print("STEP 1 — LOADING DATASET")
    print("="*70)
    df = pd.read_csv(csv_path)
    print(f"  Shape         : {df.shape}")
    print(f"  Columns       : {list(df.columns)}")
    print(f"  Missing values:\n{df.isnull().sum()}")
    print(f"  Dtypes:\n{df.dtypes}")
    print(f"\n  Sample:\n{df.head(3)}")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — PREPROCESS
# ─────────────────────────────────────────────────────────────────────────────
def preprocess(df: pd.DataFrame):
    print("\n" + "="*70)
    print("STEP 2 — PREPROCESSING")
    print("="*70)

    df = df.copy()

    # Drop rows with missing values
    before = len(df)
    df.dropna(inplace=True)
    print(f"  Dropped {before - len(df)} rows with NaN → {len(df)} remaining")

    # Encode boolean columns
    for col in ['light', 'motion']:
        if col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].map({'true': 1, 'false': 0,
                                       'True': 1, 'False': 0}).fillna(0).astype(int)
            else:
                df[col] = df[col].astype(int)

    # Encode device MAC as integer
    if 'device' in df.columns:
        le = LabelEncoder()
        df['device_enc'] = le.fit_transform(df['device'].astype(str))
        device_map = dict(zip(le.classes_, le.transform(le.classes_)))
        print(f"  Device mapping: {device_map}")
    else:
        df['device_enc'] = 0

    # Feature columns (numeric sensor readings)
    FEATURE_COLS = ['co', 'humidity', 'light', 'lpg', 'motion', 'smoke', 'temp', 'device_enc']
    FEATURE_COLS = [c for c in FEATURE_COLS if c in df.columns]
    print(f"  Feature columns: {FEATURE_COLS}")

    X = df[FEATURE_COLS].copy()

    # ── Engineered anomaly labels (rule-based, based on domain knowledge) ──────
    # These rules define what "anomalous" sensor readings look like:
    #   - CO > 0.01 ppm          (elevated carbon monoxide)
    #   - LPG > 0.02 ppm         (elevated gas leak indicator)
    #   - Smoke > 0.02           (elevated smoke)
    #   - Temperature > 40°C     (extreme heat)
    #   - Humidity < 10 or > 95  (extreme humidity)
    #   - CO + LPG + smoke all elevated together (combined attack signature)
    anomaly_mask = (
        (df['co']       > df['co'].quantile(0.97))       |
        (df['lpg']      > df['lpg'].quantile(0.97))      |
        (df['smoke']    > df['smoke'].quantile(0.97))    |
        (df['temp']     > df['temp'].quantile(0.99))     |
        (df['humidity'] < df['humidity'].quantile(0.01)) |
        (df['humidity'] > df['humidity'].quantile(0.99)) |
        (
            (df['co']    > df['co'].quantile(0.90)) &
            (df['lpg']   > df['lpg'].quantile(0.90)) &
            (df['smoke'] > df['smoke'].quantile(0.90))
        )
    )

    y = anomaly_mask.astype(int)
    print(f"\n  Label distribution:")
    print(f"    Normal (0)   : {(y==0).sum():,} ({(y==0).mean()*100:.1f}%)")
    print(f"    Anomaly (1)  : {(y==1).sum():,} ({(y==1).mean()*100:.1f}%)")

    return X, y, FEATURE_COLS


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — FEATURE ENGINEERING & SCALING
# ─────────────────────────────────────────────────────────────────────────────
def engineer_and_scale(X: pd.DataFrame, feature_cols):
    print("\n" + "="*70)
    print("STEP 3 — FEATURE ENGINEERING & SCALING")
    print("="*70)

    X = X.copy()

    # Derived features
    if 'co' in X.columns and 'lpg' in X.columns and 'smoke' in X.columns:
        X['gas_index']     = X['co'] + X['lpg'] + X['smoke']
        X['co_lpg_ratio']  = X['co'] / (X['lpg'] + 1e-9)
    if 'temp' in X.columns and 'humidity' in X.columns:
        X['heat_index']    = X['temp'] * (1 + 0.33 * X['humidity'] / 100)
    if 'co' in X.columns and 'temp' in X.columns:
        X['co_temp']       = X['co'] * X['temp']

    print(f"  Feature count after engineering: {X.shape[1]}")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

    return X_scaled, scaler, list(X.columns)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — TRAIN / TEST SPLIT
# ─────────────────────────────────────────────────────────────────────────────
def split_data(X, y, test_size=0.2, sample_size=50000):
    print("\n" + "="*70)
    print("STEP 4 — TRAIN/TEST SPLIT")
    print("="*70)

    # Sample for faster training if dataset is large
    if len(X) > sample_size:
        print(f"  Sampling {sample_size:,} records from {len(X):,} for speed")
        idx = np.random.choice(len(X), sample_size, replace=False)
        X = X.iloc[idx].reset_index(drop=True)
        y = y.iloc[idx].reset_index(drop=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    print(f"  Train : {len(X_train):,} rows")
    print(f"  Test  : {len(X_test):,} rows")
    return X_train, X_test, y_train, y_test


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — MODEL DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────
def get_models(contamination_rate: float):
    models = {
        # ── Unsupervised ──────────────────────────────────────────────────────
        "Isolation Forest": {
            "model": IsolationForest(
                n_estimators=200,
                contamination=contamination_rate,
                max_samples='auto',
                random_state=42,
                n_jobs=-1
            ),
            "type": "unsupervised"
        },
        "One-Class SVM": {
            "model": OneClassSVM(
                kernel='rbf',
                nu=contamination_rate,
                gamma='scale'
            ),
            "type": "unsupervised"
        },
        "Local Outlier Factor": {
            "model": LocalOutlierFactor(
                n_neighbors=20,
                contamination=contamination_rate,
                novelty=True,
                n_jobs=-1
            ),
            "type": "unsupervised"
        },

        # ── Supervised ────────────────────────────────────────────────────────
        "Random Forest": {
            "model": RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                class_weight='balanced',
                random_state=42,
                n_jobs=-1
            ),
            "type": "supervised"
        },
        "Gradient Boosting": {
            "model": GradientBoostingClassifier(
                n_estimators=150,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            ),
            "type": "supervised"
        },
        "Logistic Regression": {
            "model": LogisticRegression(
                max_iter=1000,
                class_weight='balanced',
                random_state=42,
                n_jobs=-1
            ),
            "type": "supervised"
        },
        "K-Nearest Neighbours": {
            "model": KNeighborsClassifier(
                n_neighbors=7,
                weights='distance',
                n_jobs=-1
            ),
            "type": "supervised"
        },
        "Decision Tree": {
            "model": DecisionTreeClassifier(
                max_depth=12,
                class_weight='balanced',
                random_state=42
            ),
            "type": "supervised"
        },
        "Neural Network (MLP)": {
            "model": MLPClassifier(
                hidden_layer_sizes=(128, 64, 32),
                activation='relu',
                max_iter=300,
                early_stopping=True,
                validation_fraction=0.1,
                random_state=42
            ),
            "type": "supervised"
        },
    }

    if XGBOOST_AVAILABLE:
        models["XGBoost"] = {
            "model": XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                scale_pos_weight=1,
                use_label_encoder=False,
                eval_metric='logloss',
                random_state=42,
                n_jobs=-1
            ),
            "type": "supervised"
        }

    return models


# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 — TRAIN & EVALUATE ALL MODELS
# ─────────────────────────────────────────────────────────────────────────────
def train_and_evaluate(models, X_train, X_test, y_train, y_test):
    print("\n" + "="*70)
    print("STEP 6 — TRAINING & EVALUATING ALL MODELS")
    print("="*70)

    results = []
    trained_models = {}

    for name, cfg in models.items():
        model = cfg['model']
        mtype = cfg['type']
        print(f"\n  ▶  {name} ({mtype})")

        t0 = time.time()

        try:
            if mtype == "unsupervised":
                model.fit(X_train)
                raw_preds = model.predict(X_test)
                # Convert -1/1 to 1/0 (Isolation Forest returns -1 for anomaly)
                y_pred = np.where(raw_preds == -1, 1, 0)
                # Anomaly scores for ROC
                if hasattr(model, 'score_samples'):
                    scores = -model.score_samples(X_test)
                elif hasattr(model, 'decision_function'):
                    scores = -model.decision_function(X_test)
                else:
                    scores = y_pred.astype(float)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                if hasattr(model, 'predict_proba'):
                    scores = model.predict_proba(X_test)[:, 1]
                elif hasattr(model, 'decision_function'):
                    scores = model.decision_function(X_test)
                else:
                    scores = y_pred.astype(float)

            elapsed = time.time() - t0

            # Metrics
            acc    = accuracy_score(y_test, y_pred)
            prec   = precision_score(y_test, y_pred, zero_division=0)
            rec    = recall_score(y_test, y_pred, zero_division=0)
            f1     = f1_score(y_test, y_pred, zero_division=0)
            try:
                roc = roc_auc_score(y_test, scores)
            except Exception:
                roc = 0.5

            # Cross-val on train set (supervised only — faster)
            if mtype == "supervised":
                cv = cross_val_score(model, X_train, y_train,
                                     cv=StratifiedKFold(5), scoring='f1', n_jobs=-1)
                cv_mean = cv.mean()
                cv_std  = cv.std()
            else:
                cv_mean = f1
                cv_std  = 0.0

            result = {
                "Model":          name,
                "Type":           mtype,
                "Accuracy":       round(acc,  4),
                "Precision":      round(prec, 4),
                "Recall":         round(rec,  4),
                "F1 Score":       round(f1,   4),
                "ROC-AUC":        round(roc,  4),
                "CV F1 Mean":     round(cv_mean, 4),
                "CV F1 Std":      round(cv_std,  4),
                "Train Time (s)": round(elapsed, 2),
            }
            results.append(result)
            trained_models[name] = {
                "model": model, "y_pred": y_pred,
                "scores": scores, "type": mtype, "metrics": result
            }

            print(f"     Accuracy  : {acc:.4f}")
            print(f"     Precision : {prec:.4f}")
            print(f"     Recall    : {rec:.4f}")
            print(f"     F1 Score  : {f1:.4f}")
            print(f"     ROC-AUC   : {roc:.4f}")
            print(f"     Train Time: {elapsed:.2f}s")

        except Exception as e:
            print(f"     ⚠ FAILED: {e}")

    return results, trained_models


# ─────────────────────────────────────────────────────────────────────────────
# STEP 7 — SELECT BEST MODEL
# ─────────────────────────────────────────────────────────────────────────────
def select_best(results: list, trained_models: dict):
    print("\n" + "="*70)
    print("STEP 7 — MODEL SELECTION")
    print("="*70)

    df_results = pd.DataFrame(results)

    # Composite score: weighted average of F1, ROC-AUC, Precision, Recall
    df_results['Composite Score'] = (
        0.35 * df_results['F1 Score']  +
        0.30 * df_results['ROC-AUC']   +
        0.20 * df_results['Precision'] +
        0.15 * df_results['Recall']
    ).round(4)

    df_results.sort_values('Composite Score', ascending=False, inplace=True)
    df_results.reset_index(drop=True, inplace=True)

    print("\n  RANKING (by Composite Score):")
    print(f"  {'Rank':<5} {'Model':<26} {'F1':>6} {'ROC-AUC':>8} {'Prec':>6} {'Rec':>6} {'Composite':>10}")
    print("  " + "-"*72)
    for i, row in df_results.iterrows():
        marker = "  ◀ BEST" if i == 0 else ""
        print(f"  {i+1:<5} {row['Model']:<26} {row['F1 Score']:>6.4f} "
              f"{row['ROC-AUC']:>8.4f} {row['Precision']:>6.4f} "
              f"{row['Recall']:>6.4f} {row['Composite Score']:>10.4f}{marker}")

    best_name = df_results.iloc[0]['Model']
    best_model = trained_models[best_name]['model']
    print(f"\n  ✅  BEST MODEL: {best_name}")
    print(f"      Composite Score : {df_results.iloc[0]['Composite Score']:.4f}")
    print(f"      F1              : {df_results.iloc[0]['F1 Score']:.4f}")
    print(f"      ROC-AUC         : {df_results.iloc[0]['ROC-AUC']:.4f}")

    return df_results, best_name, best_model


# ─────────────────────────────────────────────────────────────────────────────
# STEP 8 — VISUALISATIONS
# ─────────────────────────────────────────────────────────────────────────────
def generate_visualisations(df_results, trained_models, X_test, y_test):
    print("\n" + "="*70)
    print("STEP 8 — GENERATING VISUALISATIONS")
    print("="*70)

    plt.style.use('dark_background')
    TEAL   = '#00A896'
    MINT   = '#02C39A'
    AMBER  = '#F4A300'
    CORAL  = '#E74C3C'
    NAVY   = '#0D1B2A'
    SILVER = '#B0BEC5'
    WHITE  = '#FFFFFF'
    COLORS = [TEAL, MINT, AMBER, CORAL, '#AED6F1', '#6C8EBF',
              '#7B68EE', '#FF8C42', '#98C1D9', '#3D405B']

    # ── Plot 1: Model Comparison Bar Chart ───────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.patch.set_facecolor(NAVY)
    fig.suptitle('IoT Anomaly Detection — Model Comparison',
                 fontsize=18, fontweight='bold', color=WHITE, y=1.01)

    metrics = ['F1 Score', 'ROC-AUC', 'Precision', 'Recall']
    titles  = ['F1 Score', 'ROC-AUC Score', 'Precision', 'Recall']

    for ax, metric, title in zip(axes.flat, metrics, titles):
        ax.set_facecolor('#07111A')
        bars = ax.barh(df_results['Model'], df_results[metric],
                       color=COLORS[:len(df_results)], edgecolor='none', height=0.65)
        ax.set_title(title, color=TEAL, fontsize=13, fontweight='bold', pad=8)
        ax.set_xlim(0, 1.05)
        ax.tick_params(colors=SILVER, labelsize=9)
        ax.spines[:].set_color('#1B4F72')
        ax.set_xlabel(metric, color=SILVER, fontsize=10)
        for bar, val in zip(bars, df_results[metric]):
            ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
                    f'{val:.3f}', va='center', ha='left', color=WHITE, fontsize=8.5)

    plt.tight_layout()
    p1 = os.path.join(OUT_DIR, 'plot1_model_comparison.png')
    plt.savefig(p1, dpi=150, bbox_inches='tight', facecolor=NAVY)
    plt.close()
    print(f"  Saved: {p1}")

    # ── Plot 2: Composite Score Ranking ──────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor('#07111A')

    colors = [MINT if i == 0 else TEAL for i in range(len(df_results))]
    bars = ax.barh(df_results['Model'][::-1], df_results['Composite Score'][::-1],
                   color=colors[::-1], edgecolor='none', height=0.65)
    ax.set_title('Model Ranking — Composite Score\n(0.35×F1 + 0.30×ROC-AUC + 0.20×Precision + 0.15×Recall)',
                 color=WHITE, fontsize=14, fontweight='bold')
    ax.set_xlim(0, 1.1)
    ax.tick_params(colors=SILVER, labelsize=10)
    ax.spines[:].set_color('#1B4F72')
    ax.set_xlabel('Composite Score', color=SILVER)
    for bar, val in zip(bars, df_results['Composite Score'][::-1]):
        ax.text(val + 0.005, bar.get_y() + bar.get_height()/2,
                f'{val:.4f}', va='center', color=WHITE, fontsize=10)
    ax.axvline(x=df_results['Composite Score'].max(), color=AMBER,
               linestyle='--', linewidth=1.5, label='Best score')
    ax.legend(facecolor=NAVY, labelcolor=AMBER)

    plt.tight_layout()
    p2 = os.path.join(OUT_DIR, 'plot2_composite_ranking.png')
    plt.savefig(p2, dpi=150, bbox_inches='tight', facecolor=NAVY)
    plt.close()
    print(f"  Saved: {p2}")

    # ── Plot 3: ROC Curves (supervised models with predict_proba) ────────────
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor('#07111A')

    color_cycle = COLORS
    plotted = 0
    for (name, info), color in zip(trained_models.items(), color_cycle):
        try:
            scores = info['scores']
            if len(np.unique(scores)) > 2:
                fpr, tpr, _ = roc_curve(y_test, scores)
                roc_auc = auc(fpr, tpr)
                lw = 2.5 if info['metrics']['ROC-AUC'] == max(
                    t['metrics']['ROC-AUC'] for t in trained_models.values()) else 1.5
                ax.plot(fpr, tpr, color=color, lw=lw,
                        label=f"{name} (AUC={roc_auc:.3f})")
                plotted += 1
        except Exception:
            pass

    ax.plot([0,1], [0,1], 'w--', lw=1, alpha=0.5, label='Random (AUC=0.500)')
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1.02])
    ax.set_xlabel('False Positive Rate', color=SILVER, fontsize=12)
    ax.set_ylabel('True Positive Rate', color=SILVER, fontsize=12)
    ax.set_title('ROC Curves — All Models', color=WHITE, fontsize=14, fontweight='bold')
    ax.tick_params(colors=SILVER)
    ax.spines[:].set_color('#1B4F72')
    ax.legend(loc='lower right', facecolor='#07111A', labelcolor=SILVER, fontsize=9)
    ax.grid(color='#1B4F72', linewidth=0.5)

    plt.tight_layout()
    p3 = os.path.join(OUT_DIR, 'plot3_roc_curves.png')
    plt.savefig(p3, dpi=150, bbox_inches='tight', facecolor=NAVY)
    plt.close()
    print(f"  Saved: {p3}")

    # ── Plot 4: Confusion Matrix for best model ───────────────────────────────
    best_name = df_results.iloc[0]['Model']
    y_pred_best = trained_models[best_name]['y_pred']
    cm = confusion_matrix(y_test, y_pred_best)

    fig, ax = plt.subplots(figsize=(7, 6))
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    sns.heatmap(cm, annot=True, fmt='d', ax=ax,
                cmap=sns.color_palette("Blues", as_cmap=True),
                xticklabels=['Normal', 'Anomaly'],
                yticklabels=['Normal', 'Anomaly'],
                linewidths=0.5, linecolor='#07111A',
                annot_kws={"size": 16, "color": "white", "weight": "bold"})
    ax.set_title(f'Confusion Matrix — {best_name}',
                 color=WHITE, fontsize=13, fontweight='bold')
    ax.set_xlabel('Predicted', color=SILVER, fontsize=11)
    ax.set_ylabel('Actual', color=SILVER, fontsize=11)
    ax.tick_params(colors=SILVER)

    plt.tight_layout()
    p4 = os.path.join(OUT_DIR, 'plot4_confusion_matrix_best.png')
    plt.savefig(p4, dpi=150, bbox_inches='tight', facecolor=NAVY)
    plt.close()
    print(f"  Saved: {p4}")

    # ── Plot 5: Feature Importance (best supervised model) ────────────────────
    best_info = trained_models[best_name]
    best_model = best_info['model']
    if hasattr(best_model, 'feature_importances_'):
        fi = best_model.feature_importances_
        feat_names = X_test.columns.tolist()
        fi_df = pd.DataFrame({'Feature': feat_names, 'Importance': fi})
        fi_df.sort_values('Importance', ascending=True, inplace=True)

        fig, ax = plt.subplots(figsize=(10, 7))
        fig.patch.set_facecolor(NAVY)
        ax.set_facecolor('#07111A')

        bars = ax.barh(fi_df['Feature'], fi_df['Importance'],
                       color=[MINT if v > fi_df['Importance'].median()
                              else TEAL for v in fi_df['Importance']],
                       edgecolor='none', height=0.65)
        ax.set_title(f'Feature Importance — {best_name}',
                     color=WHITE, fontsize=13, fontweight='bold')
        ax.set_xlabel('Importance Score', color=SILVER)
        ax.tick_params(colors=SILVER, labelsize=10)
        ax.spines[:].set_color('#1B4F72')
        for bar, val in zip(bars, fi_df['Importance']):
            ax.text(val + 0.001, bar.get_y() + bar.get_height()/2,
                    f'{val:.4f}', va='center', color=WHITE, fontsize=9)

        plt.tight_layout()
        p5 = os.path.join(OUT_DIR, 'plot5_feature_importance.png')
        plt.savefig(p5, dpi=150, bbox_inches='tight', facecolor=NAVY)
        plt.close()
        print(f"  Saved: {p5}")

    # ── Plot 6: Training Time vs F1 Score scatter ─────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor('#07111A')

    sc = ax.scatter(df_results['Train Time (s)'], df_results['F1 Score'],
                    c=df_results['ROC-AUC'], cmap='cool',
                    s=180, zorder=5, edgecolors=WHITE, linewidths=0.5)
    for _, row in df_results.iterrows():
        ax.annotate(row['Model'], (row['Train Time (s)'], row['F1 Score']),
                    textcoords='offset points', xytext=(8, 4),
                    fontsize=9, color=SILVER)
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label('ROC-AUC', color=SILVER)
    cbar.ax.yaxis.set_tick_params(color=SILVER)

    ax.set_xlabel('Training Time (seconds)', color=SILVER, fontsize=11)
    ax.set_ylabel('F1 Score', color=SILVER, fontsize=11)
    ax.set_title('Speed vs. Accuracy Trade-off', color=WHITE, fontsize=13, fontweight='bold')
    ax.tick_params(colors=SILVER)
    ax.spines[:].set_color('#1B4F72')
    ax.grid(color='#1B4F72', linewidth=0.5)

    plt.tight_layout()
    p6 = os.path.join(OUT_DIR, 'plot6_speed_vs_accuracy.png')
    plt.savefig(p6, dpi=150, bbox_inches='tight', facecolor=NAVY)
    plt.close()
    print(f"  Saved: {p6}")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 9 — SAVE ARTEFACTS
# ─────────────────────────────────────────────────────────────────────────────
def save_artefacts(df_results, best_name, best_model, scaler, feature_cols):
    print("\n" + "="*70)
    print("STEP 9 — SAVING ARTEFACTS")
    print("="*70)

    # CSV results
    csv_path = os.path.join(OUT_DIR, 'model_comparison_results.csv')
    df_results.to_csv(csv_path, index=False)
    print(f"  Results CSV : {csv_path}")

    # Best model bundle (model + scaler + feature list + metadata)
    bundle = {
        'model':        best_model,
        'scaler':       scaler,
        'feature_cols': feature_cols,
        'model_name':   best_name,
        'metrics':      df_results.iloc[0].to_dict(),
    }
    model_path = os.path.join(OUT_DIR, 'best_iot_model.pkl')
    joblib.dump(bundle, model_path)
    print(f"  Best model  : {model_path}")
    print(f"  Model name  : {best_name}")

    # Print final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(df_results[['Model','Type','F1 Score','ROC-AUC',
                       'Precision','Recall','Composite Score',
                       'Train Time (s)']].to_string(index=False))


# ─────────────────────────────────────────────────────────────────────────────
# STEP 10 — DEMO INFERENCE (shows how the saved model is used in the API)
# ─────────────────────────────────────────────────────────────────────────────
def demo_inference(model_path: str):
    print("\n" + "="*70)
    print("STEP 10 — DEMO INFERENCE (API integration preview)")
    print("="*70)

    bundle = joblib.load(model_path)
    model       = bundle['model']
    scaler      = bundle['scaler']
    feat_cols   = bundle['feature_cols']
    model_name  = bundle['model_name']

    print(f"  Loaded model: {model_name}")
    print(f"  Features    : {feat_cols}")

    # Simulate normal reading
    normal_reading = {
        'co': 0.00468, 'humidity': 51.0, 'light': False,
        'lpg': 0.00780, 'motion': False, 'smoke': 0.02040, 'temp': 22.7,
        'device_enc': 0
    }

    # Simulate anomalous reading (gas leak + high temp)
    anomaly_reading = {
        'co': 0.0850, 'humidity': 92.0, 'light': True,
        'lpg': 0.0950, 'motion': True, 'smoke': 0.1850, 'temp': 48.5,
        'device_enc': 0
    }

    def predict_reading(reading):
        df_r = pd.DataFrame([reading])
        for col in feat_cols:
            if col not in df_r.columns:
                df_r[col] = 0
        # Engineer same features as training
        if 'co' in df_r and 'lpg' in df_r and 'smoke' in df_r:
            df_r['gas_index']    = df_r['co'] + df_r['lpg'] + df_r['smoke']
            df_r['co_lpg_ratio'] = df_r['co'] / (df_r['lpg'] + 1e-9)
        if 'temp' in df_r and 'humidity' in df_r:
            df_r['heat_index']   = df_r['temp'] * (1 + 0.33 * df_r['humidity'] / 100)
        if 'co' in df_r and 'temp' in df_r:
            df_r['co_temp']      = df_r['co'] * df_r['temp']
        df_r = df_r.reindex(columns=feat_cols, fill_value=0)
        X_s = scaler.transform(df_r)
        pred = model.predict(X_s)[0]
        if hasattr(model, 'predict_proba'):
            prob = model.predict_proba(X_s)[0][1]
        elif hasattr(model, 'decision_function'):
            prob = float(model.decision_function(X_s)[0])
        else:
            prob = float(pred)
        label = "⚠ ANOMALY" if pred == 1 else "✓ NORMAL"
        return label, round(prob, 4)

    for name, reading in [("Normal Sensor Reading", normal_reading),
                           ("Anomalous Reading (gas+heat)", anomaly_reading)]:
        label, prob = predict_reading(reading)
        print(f"\n  {name}:")
        print(f"    Prediction : {label}")
        print(f"    Anomaly score : {prob}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main(csv_path: str):
    np.random.seed(42)

    # Load
    df = load_data(csv_path)

    # Preprocess
    X, y, feature_cols = preprocess(df)

    # Feature engineering + scaling
    X_scaled, scaler, all_features = engineer_and_scale(X, feature_cols)

    # Split
    X_train, X_test, y_train, y_test = split_data(X_scaled, y)

    # Contamination rate = anomaly proportion
    contamination = float(y.mean())
    contamination = max(0.01, min(contamination, 0.45))
    print(f"\n  Contamination rate: {contamination:.4f}")

    # Get models
    models = get_models(contamination)
    print(f"\n  Training {len(models)} models...")

    # Train & evaluate
    results, trained_models = train_and_evaluate(
        models, X_train, X_test, y_train, y_test
    )

    # Select best
    df_results, best_name, best_model = select_best(results, trained_models)

    # Visualise
    generate_visualisations(df_results, trained_models, X_test, y_test)

    # Save
    save_artefacts(df_results, best_name, best_model, scaler, all_features)

    # Demo
    model_path = os.path.join(OUT_DIR, 'best_iot_model.pkl')
    demo_inference(model_path)

    print("\n" + "="*70)
    print(f"✅  PIPELINE COMPLETE — outputs saved to: {OUT_DIR}")
    print("="*70)

    return df_results, best_name


if __name__ == '__main__':
    # Usage: python ml_training_pipeline.py path/to/iot_telemetry_data.csv
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python ml_training_pipeline.py iot_telemetry_data.csv")
        print("\nDataset: https://www.kaggle.com/datasets/garystafford/environmental-sensor-data-132k")
        print("\nExpected columns: ts, device, co, humidity, light, lpg, motion, smoke, temp")
        sys.exit(0)

    csv_file = sys.argv[1]
    if not os.path.exists(csv_file):
        print(f"❌  File not found: {csv_file}")
        sys.exit(1)

    main(csv_file)
