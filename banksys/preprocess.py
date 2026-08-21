"""特征预处理(US-3):离线训练与在线预测共用同一编码管线。"""

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

from banksys.data import CATEGORICAL_COLS, FEATURE_COLS, NUMERIC_COLS

# 训练集中出现的合法取值,unknown 保留为真实类别
UNKNOWN = "unknown"


class InputValidationError(ValueError):
    """用户输入缺失/非法时抛出,页面据此展示友好提示。"""


def build_preprocessor() -> Pipeline:
    """类别特征 Ordinal 编码;数值特征原样透传。

    handle_unknown="use_encoded_value" + unknown_value=-1:
    在线预测遇到训练集未出现的类别时编码为 -1,不崩溃。
    """
    return Pipeline(
        steps=[
            (
                "encode",
                ColumnTransformer(
                    transformers=[
                        (
                            "cat",
                            OrdinalEncoder(
                                handle_unknown="use_encoded_value",
                                unknown_value=-1,
                            ),
                            CATEGORICAL_COLS,
                        )
                    ],
                    remainder="passthrough",
                ),
            )
        ]
    )


def fit_preprocessor(df: pd.DataFrame) -> Pipeline:
    """基于训练数据 fit 编码器,返回可复用管线。

    fit 与 transform 都传完整 FEATURE_COLS:编码器只处理类别列,
    数值列由 ColumnTransformer 的 passthrough 透传。
    """
    pre = build_preprocessor()
    pre.fit(df[FEATURE_COLS])
    return pre


def transform_features(pre: Pipeline, df: pd.DataFrame) -> pd.DataFrame:
    """将特征 DataFrame 编码为特征矩阵(列名固定为 FEATURE_COLS)。"""
    encoded = pre.transform(df[FEATURE_COLS])
    return pd.DataFrame(encoded, columns=FEATURE_COLS)


def validate_input(features: dict) -> None:
    """校验单条用户输入:特征齐全、数值列可转 float。"""
    missing = [c for c in FEATURE_COLS if c not in features]
    if missing:
        raise InputValidationError(f"缺少特征:{missing}")

    for col in NUMERIC_COLS:
        try:
            float(features[col])
        except (TypeError, ValueError) as exc:
            raise InputValidationError(f"{col} 必须是数字,收到 {features[col]!r}") from exc


def features_to_frame(features: dict) -> pd.DataFrame:
    """单条输入 dict → 一行特征 DataFrame(按训练列顺序)。"""
    validate_input(features)
    return pd.DataFrame([{c: features[c] for c in FEATURE_COLS}])
