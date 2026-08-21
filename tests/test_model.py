"""模型训练、存取与推理测试(US-4)。"""

import json

import pytest

from banksys.data import CATEGORICAL_COLS, FEATURE_COLS, TARGET_COL, load_data
from banksys.model import (
    METRICS_FILENAME,
    build_model,
    evaluate,
    load_pipeline,
    predict,
    save_pipeline,
)
from banksys.preprocess import fit_preprocessor, transform_features


@pytest.fixture(scope="module")
def trained(tmp_path_factory):
    """小样本 + 少树快速训练,供推理/存取测试复用。"""
    df = load_data("train").sample(n=2000, random_state=42)
    y = (df[TARGET_COL] == "yes").astype(int)
    pre = fit_preprocessor(df)
    X = transform_features(pre, df)
    model = build_model(n_estimators=10)
    model.fit(X, y)
    return model, pre, X, y


def test_build_model_is_reproducible():
    m1 = build_model(n_estimators=5)
    m2 = build_model(n_estimators=5)
    assert m1.get_params()["random_state"] == m2.get_params()["random_state"] == 42


def test_evaluate_returns_metrics_in_range(trained):
    model, _, X, y = trained
    metrics = evaluate(model, X, y)

    assert 0.0 <= metrics["auc"] <= 1.0
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert "report" in metrics


def test_save_and_load_roundtrip(trained, tmp_path):
    model, pre, X, y = trained
    metrics = evaluate(model, X, y)
    save_pipeline(model, pre, metrics, out_dir=tmp_path)

    assert (tmp_path / "model.joblib").exists()
    assert (tmp_path / "preprocessor.joblib").exists()
    loaded_metrics = json.loads((tmp_path / METRICS_FILENAME).read_text(encoding="utf-8"))
    assert loaded_metrics["auc"] == pytest.approx(metrics["auc"])

    model2, pre2 = load_pipeline(tmp_path)
    assert (model2.predict(X) == model.predict(X)).all()


def test_load_pipeline_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="模型产物缺失"):
        load_pipeline(tmp_path)


def test_predict_returns_label_and_probability(trained):
    model, pre, _, _ = trained
    sample = load_data("train").iloc[0]
    features = {c: sample[c] for c in FEATURE_COLS}

    result = predict(model, pre, features)

    assert set(result) == {"subscribe", "label", "probability"}
    assert result["label"] in {"yes", "no"}
    assert result["subscribe"] is (result["label"] == "yes")
    assert 0.0 <= result["probability"] <= 1.0


def test_predict_unknown_category_does_not_crash(trained):
    model, pre, _, _ = trained
    sample = load_data("train").iloc[0]
    features = {c: sample[c] for c in FEATURE_COLS}
    for col in CATEGORICAL_COLS:
        features[col] = "never-seen"

    result = predict(model, pre, features)

    assert result["label"] in {"yes", "no"}


def test_predict_invalid_input_raises(trained):
    model, pre, _, _ = trained
    sample = load_data("train").iloc[0]
    features = {c: sample[c] for c in FEATURE_COLS}
    features["age"] = "old"

    with pytest.raises(ValueError, match="age 必须是数字"):
        predict(model, pre, features)
