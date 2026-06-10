"""
=============================================================================
ml_module.py  — IoT Blockchain Security System
=============================================================================
Drop this file into your existing project alongside app.py.
It loads the trained best model and exposes:
  - MLPredictor class  (used inside /api/register)
  - /api/predict       (standalone prediction endpoint)
  - /api/ml/stats      (model metadata + detection stats)

Integration into your existing app.py:
  from ml_module import MLPredictor, ml_blueprint
  app.register_blueprint(ml_blueprint)
  ml = MLPredictor('ml_outputs/best_iot_model.pkl')
=============================================================================
"""

import os
import json
import time
import numpy as np
import pandas as pd
import joblib

from flask import Blueprint, request, jsonify

# ── Blueprint (registers /api/predict and /api/ml/stats) ─────────────────────
ml_blueprint = Blueprint('ml', __name__)

# Runtime counters
_stats = {
    "total_predictions": 0,
    "anomalies_detected": 0,
    "normal_records":     0,
    "model_name":         "Not loaded",
    "model_loaded":       False,
}


# ─────────────────────────────────────────────────────────────────────────────
class MLPredictor:
    """
    Loads the saved best_iot_model.pkl bundle and provides predict().
    Compatible with all 10 model types trained by ml_training_pipeline.py.

    Usage:
        ml = MLPredictor('ml_outputs/best_iot_model.pkl')
        result = ml.predict({'co': 0.005, 'humidity': 51, 'temp': 22.7, ...})
        # result = {
        #   'is_anomaly': False,
        #   'anomaly_score': 0.032,
        #   'label': 'NORMAL',
        #   'confidence': 0.97,
        #   'model': 'Random Forest',
        #   'latency_ms': 1.4
        # }
    """

    FEATURE_DEFAULTS = {
        'co': 0.0, 'humidity': 50.0, 'light': 0,
        'lpg': 0.0, 'motion': 0, 'smoke': 0.0,
        'temp': 25.0, 'device_enc': 0
    }

    def __init__(self, model_path: str):
        self.model_path   = model_path
        self.model        = None
        self.scaler       = None
        self.feature_cols = None
        self.model_name   = None
        self.metrics      = {}
        self._loaded      = False
        self._load()

    def _load(self):
        if not os.path.exists(self.model_path):
            print(f"[ML] ⚠  Model file not found: {self.model_path}")
            print("[ML]    Run ml_training_pipeline.py first to train models.")
            return
        try:
            bundle            = joblib.load(self.model_path)
            self.model        = bundle['model']
            self.scaler       = bundle['scaler']
            self.feature_cols = bundle['feature_cols']
            self.model_name   = bundle['model_name']
            self.metrics      = bundle.get('metrics', {})
            self._loaded      = True
            _stats['model_name']   = self.model_name
            _stats['model_loaded'] = True
            print(f"[ML] ✅  Loaded best model: {self.model_name}")
            print(f"[ML]    F1={self.metrics.get('F1 Score','?')}  "
                  f"ROC-AUC={self.metrics.get('ROC-AUC','?')}")
        except Exception as e:
            print(f"[ML] ❌  Failed to load model: {e}")

    def _build_feature_row(self, sensor_data: dict) -> pd.DataFrame:
        """Convert raw sensor dict → scaled feature row ready for inference."""
        row = {}

        # Base features — with frontend field name aliases
    aliases = {
        'temp':       ['temp', 'temperature'],
        'co':         ['co', 'carbon_monoxide'],
        'humidity':   ['humidity'],
        'smoke':      ['smoke'],
        'lpg':        ['lpg'],
        'light':      ['light'],
        'motion':     ['motion'],
        'device_enc': ['device_enc'],
    }
    for col, keys in aliases.items():
        val = None
        for key in keys:
            if key in sensor_data:
                val = sensor_data[key]
                break
        if val is None:
            val = self.FEATURE_DEFAULTS.get(col, 0)
        if isinstance(val, bool):
            val = int(val)
        elif isinstance(val, str):
            val = 1 if val.lower() in ('true', '1', 'yes') else 0
        row[col] = float(val)

        df_r = pd.DataFrame([row])

        # Engineered features (must match training pipeline exactly)
        if all(c in df_r for c in ['co', 'lpg', 'smoke']):
            df_r['gas_index']    = df_r['co'] + df_r['lpg'] + df_r['smoke']
            df_r['co_lpg_ratio'] = df_r['co'] / (df_r['lpg'] + 1e-9)
        if all(c in df_r for c in ['temp', 'humidity']):
            df_r['heat_index'] = df_r['temp'] * (1 + 0.33 * df_r['humidity'] / 100)
        if all(c in df_r for c in ['co', 'temp']):
            df_r['co_temp'] = df_r['co'] * df_r['temp']

        # Align to exact training columns
        df_r = df_r.reindex(columns=self.feature_cols, fill_value=0.0)

        # Scale
        X_scaled = self.scaler.transform(df_r)
        return X_scaled

    def predict(self, sensor_data: dict) -> dict:
        """
        Run ML prediction on a sensor reading.

        Returns dict with:
          is_anomaly    (bool)
          anomaly_score (float 0–1)
          label         ('ANOMALY' | 'NORMAL')
          confidence    (float 0–1)
          model         (str)
          latency_ms    (float)
        """
        if not self._loaded:
            return {
                'is_anomaly': False, 'anomaly_score': 0.0,
                'label': 'ML_NOT_LOADED', 'confidence': 0.0,
                'model': 'None', 'latency_ms': 0.0
            }

        t0 = time.time()
        try:
            X = self._build_feature_row(sensor_data)
            raw_pred = self.model.predict(X)[0]

            # Handle unsupervised models that return -1/1
            if raw_pred == -1:
                raw_pred = 1

            is_anomaly = bool(raw_pred == 1)

            # Confidence / anomaly score
            if hasattr(self.model, 'predict_proba'):
                probs     = self.model.predict_proba(X)[0]
                score     = float(probs[1])
                confidence= float(max(probs))
            elif hasattr(self.model, 'score_samples'):
                raw_score = float(-self.model.score_samples(X)[0])
                score     = min(max(raw_score / 0.5, 0.0), 1.0)
                confidence= score if is_anomaly else 1 - score
            elif hasattr(self.model, 'decision_function'):
                raw_score = float(self.model.decision_function(X)[0])
                score     = min(max(-raw_score, 0.0), 1.0)
                confidence= score if is_anomaly else 1 - score
            else:
                score      = 1.0 if is_anomaly else 0.0
                confidence = 1.0

            latency = round((time.time() - t0) * 1000, 2)

            # Update counters
            _stats['total_predictions'] += 1
            if is_anomaly:
                _stats['anomalies_detected'] += 1
            else:
                _stats['normal_records'] += 1

            return {
                'is_anomaly':    is_anomaly,
                'anomaly_score': round(score, 4),
                'label':         'ANOMALY' if is_anomaly else 'NORMAL',
                'confidence':    round(confidence, 4),
                'model':         self.model_name,
                'latency_ms':    latency,
            }

        except Exception as e:
            return {
                'is_anomaly': False, 'anomaly_score': 0.0,
                'label': f'ERROR: {str(e)}', 'confidence': 0.0,
                'model': self.model_name, 'latency_ms': 0.0
            }

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def info(self) -> dict:
        return {
            'model_name':   self.model_name,
            'loaded':       self._loaded,
            'feature_cols': self.feature_cols,
            'metrics': {
                'f1_score':  self.metrics.get('F1 Score'),
                'roc_auc':   self.metrics.get('ROC-AUC'),
                'precision': self.metrics.get('Precision'),
                'recall':    self.metrics.get('Recall'),
                'accuracy':  self.metrics.get('Accuracy'),
            }
        }


# ─────────────────────────────────────────────────────────────────────────────
# FLASK ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

# Global predictor instance (initialised in app.py after blueprint registration)
_predictor: MLPredictor = None

def init_predictor(model_path: str):
    """Call this from app.py after app.register_blueprint(ml_blueprint)."""
    global _predictor
    _predictor = MLPredictor(model_path)
    return _predictor


@ml_blueprint.route('/predict', methods=['GET', 'POST'])
def predict():
    """
    Standalone prediction endpoint — no blockchain registration.

    Request JSON:
      {
        "device_id": "b8:27:eb:bf:9d:51",
        "sensor_data": {
          "co": 0.00468, "humidity": 51.0, "light": false,
          "lpg": 0.00780, "motion": false, "smoke": 0.0204, "temp": 22.7
        }
      }

    Response:
      {
        "device_id": "b8:27:eb:bf:9d:51",
        "prediction": {
          "is_anomaly": false,
          "anomaly_score": 0.032,
          "label": "NORMAL",
          "confidence": 0.968,
          "model": "Random Forest",
          "latency_ms": 1.4
        },
        "recommendation": "Safe to register on blockchain"
      }
    """
    if _predictor is None:
        return jsonify({'error': 'ML module not initialised'}), 503

    body = request.get_json(silent=True) or {}
    sensor_data = body.get('sensor_data', body)
    device_id   = body.get('device_id', 'unknown')

    if not sensor_data:
        return jsonify({'error': 'Missing sensor_data field'}), 400

    result = _predictor.predict(sensor_data)

    recommendation = (
        "⚠ Anomaly detected — review before blockchain registration"
        if result['is_anomaly']
        else "✓ Normal reading — safe to register on blockchain"
    )

    return jsonify({
        'device_id':      device_id,
        'prediction':     result,
        'recommendation': recommendation,
    }), 200


@ml_blueprint.route('/stats', methods=['GET'])
def ml_stats():
    """Returns ML model metadata and runtime detection statistics."""
    if _predictor is None:
        return jsonify({'error': 'ML module not initialised'}), 503

    detection_rate = (
        round(_stats['anomalies_detected'] / _stats['total_predictions'] * 100, 2)
        if _stats['total_predictions'] > 0 else 0.0
    )

    return jsonify({
        'model_info': _predictor.info,
        'runtime_stats': {
            'total_predictions':  _stats['total_predictions'],
            'anomalies_detected': _stats['anomalies_detected'],
            'normal_records':     _stats['normal_records'],
            'detection_rate_pct': detection_rate,
        }
    }), 200


# ─────────────────────────────────────────────────────────────────────────────
# HOW TO INTEGRATE INTO YOUR EXISTING app.py
# ─────────────────────────────────────────────────────────────────────────────
INTEGRATION_GUIDE = """
─────────────────────────────────────────────────────────────────────────────
INTEGRATION — add these lines to your existing app.py
─────────────────────────────────────────────────────────────────────────────

# 1. Import at the top
from ml_module import ml_blueprint, init_predictor

# 2. Register blueprint after app = Flask(__name__)
app.register_blueprint(ml_blueprint)
ml = init_predictor('ml_outputs/best_iot_model.pkl')

# 3. Update your existing /api/register endpoint to call ML before hashing:

@app.route('/api/register', methods=['POST'])
def register_data():
    body        = request.get_json()
    device_id   = body.get('device_id', 'unknown')
    sensor_data = body.get('sensor_data', {})

    # ── ML check ──────────────────────────────
    ml_result = ml.predict(sensor_data)
    # ──────────────────────────────────────────

    # Existing pipeline
    data_hash = generate_hash({**sensor_data, 'device_id': device_id})
    tx_hash   = blockchain_client.register_data(data_hash, device_id)

    return jsonify({
        'success':   True,
        'device_id': device_id,
        'data_hash': data_hash,
        'tx_hash':   tx_hash,
        'ml_check':  ml_result,        # ← new field
    }), 201

─────────────────────────────────────────────────────────────────────────────
NEW API ENDPOINTS ADDED
─────────────────────────────────────────────────────────────────────────────
  POST /api/predict       — ML-only prediction, no blockchain write
  GET  /api/ml/stats      — Model info + runtime anomaly detection stats
─────────────────────────────────────────────────────────────────────────────
"""

if __name__ == '__main__':
    print(INTEGRATION_GUIDE)
