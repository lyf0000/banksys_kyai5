"""模型训练、评估、存取与推理(US-4)。"""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.pipeline import Pipeline

from banksys.data import FEATURE_COLS
from banksys.preprocess import features_to_frame

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_FILENAME = "model.joblib"
PREPROCESSOR_FILENAME = "preprocessor.joblib"
METRICS_FILENAME = "metrics.json"

RANDOM_STATE = 42
DEFAULT_TREES = 300
QUICK_TREES = 100
PROBABILITY_THRESHOLD = 0.5


def build_model(n_estimators: int = DEFAULT_TREES) -> RandomForestClassifier:
    """固定随机种子,保证训练可复现。"""
    return RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )


def evaluate(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """计算 AUC、准确率与分类报告。"""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    return {
        "auc": float(roc_auc_score(y_test, y_prob)),
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "report": report,
    }


def save_pipeline(
    model,
    preprocessor: Pipeline,
    metrics: dict,
    out_dir: Path = MODEL_DIR,
) -> None:
    """保存模型、编码器与指标(指标不达标时由 train.py 负责拦截)。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_dir / MODEL_FILENAME)
    joblib.dump(preprocessor, out_dir / PREPROCESSOR_FILENAME)
    (out_dir / METRICS_FILENAME).write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_pipeline(model_dir: Path = MODEL_DIR) -> tuple:
    """加载模型与编码器;产物缺失时抛可读错误,页面据此提示先训练。"""
    model_path = model_dir / MODEL_FILENAME
    pre_path = model_dir / PREPROCESSOR_FILENAME
    if not (model_path.exists() and pre_path.exists()):
        raise FileNotFoundError(
            f"模型产物缺失:{model_path} 与 {pre_path}。请先运行 python scripts/train.py 完成训练。"
        )
    return joblib.load(model_path), joblib.load(pre_path)


def predict(model, preprocessor: Pipeline, features: dict) -> dict:
    """单条客户特征 → 是否认购 + 概率。

    返回 {"subscribe": bool, "label": "yes"/"no", "probability": float}
    """
    frame = features_to_frame(features)
    encoded = preprocessor.transform(frame[FEATURE_COLS])
    # 与训练时一致:带列名 DataFrame,避免 sklearn feature names 警告
    encoded_df = pd.DataFrame(encoded, columns=FEATURE_COLS)
    proba = model.predict_proba(encoded_df)[0, 1]
    subscribe = proba >= PROBABILITY_THRESHOLD
    return {
        "subscribe": bool(subscribe),
        "label": "yes" if subscribe else "no",
        "probability": float(proba),
    }
