"""特征预处理测试(US-3)。"""

import pandas as pd
import pytest

from banksys.data import CATEGORICAL_COLS, FEATURE_COLS, NUMERIC_COLS, load_data
from banksys.preprocess import (
    InputValidationError,
    build_preprocessor,
    features_to_frame,
    fit_preprocessor,
    transform_features,
    validate_input,
)


@pytest.fixture(scope="module")
def train_df() -> pd.DataFrame:
    return load_data("train")


@pytest.fixture(scope="module")
def fitted(train_df: pd.DataFrame):
    return fit_preprocessor(train_df)


def test_transform_output_shape_and_columns(train_df, fitted):
    X = transform_features(fitted, train_df.head(50))

    assert X.shape == (50, 20)
    assert list(X.columns) == FEATURE_COLS
    # 数值列透传原值
    assert X["age"].iloc[0] == train_df["age"].iloc[0]


def test_unknown_category_encodes_to_minus_one(fitted):
    row = {c: "never-seen" for c in CATEGORICAL_COLS}
    row.update({c: 0 for c in NUMERIC_COLS})
    frame = pd.DataFrame([row])
    encoded = fitted.transform(frame[FEATURE_COLS])

    # 前 10 列为类别编码,全部是未知类别 → 全为 -1
    assert (encoded[:, :10] == -1).all()


def test_fit_transform_consistent_with_transform(train_df, fitted):
    # 编码器确定性:同一编码器重复 transform 一致;全量重新 fit 也一致
    frame = train_df.head(10)
    via_transform = fitted.transform(frame[FEATURE_COLS])
    via_again = fitted.transform(frame[FEATURE_COLS])
    via_refit = build_preprocessor().fit(train_df[FEATURE_COLS]).transform(frame[FEATURE_COLS])

    assert (via_transform == via_again).all()
    assert (via_transform == via_refit).all()


def test_validate_input_accepts_valid_row():
    valid = {
        **{c: "unknown" for c in CATEGORICAL_COLS},
        **{c: 1 for c in ["age", "duration", "campaign", "pdays", "previous"]},
        **{c: 1.0 for c in ["emp_var_rate", "cons_price_index", "cons_conf_index"]},
        "lending_rate3m": 1.0,
        "nr_employed": 5000.0,
    }
    validate_input(valid)  # 不抛异常即通过


def test_validate_input_rejects_missing_feature():
    with pytest.raises(InputValidationError, match="缺少特征"):
        validate_input({"age": 30})


def test_validate_input_rejects_non_numeric_age():
    features = {
        **{c: "unknown" for c in CATEGORICAL_COLS},
        **{c: 1 for c in FEATURE_COLS},
        "age": "thirty",
    }
    with pytest.raises(InputValidationError, match="age 必须是数字"):
        validate_input(features)


def test_features_to_frame_order_matches_feature_cols():
    features = {
        **{c: "unknown" for c in CATEGORICAL_COLS},
        **{c: 0 for c in ["age", "duration", "campaign", "pdays", "previous"]},
        "emp_var_rate": 0.0,
        "cons_price_index": 90.0,
        "cons_conf_index": -40.0,
        "lending_rate3m": 1.0,
        "nr_employed": 5000.0,
    }
    frame = features_to_frame(features)

    assert list(frame.columns) == FEATURE_COLS
    assert frame["age"].iloc[0] == 0
