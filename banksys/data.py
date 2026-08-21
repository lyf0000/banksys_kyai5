"""数据加载与校验(US-2):训练与页面共用同一数据口径。"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

TARGET_COL = "subscribe"
TARGET_VALUES = {"yes", "no"}

# 特征顺序固定,训练与在线预测共用
CATEGORICAL_COLS = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]
NUMERIC_COLS = [
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]
FEATURE_COLS = CATEGORICAL_COLS + NUMERIC_COLS
TRAIN_COLS = ["id"] + FEATURE_COLS + [TARGET_COL]
TEST_COLS = ["id"] + FEATURE_COLS


class DataValidationError(ValueError):
    """数据文件缺失或列名/取值不符合预期时抛出。"""


def load_data(kind: str) -> pd.DataFrame:
    """加载 train/test 数据并校验。

    kind: "train"(22,500 行,含 subscribe)或 "test"(7,500 行,无 subscribe)。
    """
    if kind == "train":
        path, expected = DATA_DIR / "train.csv", TRAIN_COLS
    elif kind == "test":
        path, expected = DATA_DIR / "test.csv", TEST_COLS
    else:
        raise ValueError(f"kind 必须是 'train' 或 'test',收到 {kind!r}")

    if not path.exists():
        raise DataValidationError(f"数据文件不存在:{path}")

    df = pd.read_csv(path)
    _validate_schema(df, expected, path.name)
    return df


def _validate_schema(df: pd.DataFrame, expected: list[str], source: str) -> None:
    # 列集合校验(顺序不敏感),特征顺序由 FEATURE_COLS 在预处理时统一
    actual = list(df.columns)
    expected_set, actual_set = set(expected), set(actual)
    missing = sorted(expected_set - actual_set)
    extra = sorted(actual_set - expected_set)
    if missing or extra:
        raise DataValidationError(
            f"{source} 列名不符:缺 {missing},多 {extra}(期望 {len(expected)} 列)"
        )

    null_cols = [c for c in df.columns if df[c].isna().any()]
    if null_cols:
        raise DataValidationError(f"{source} 存在空值列:{null_cols}")


def validate_train_target(df: pd.DataFrame) -> None:
    """校验训练集目标列取值只含 yes/no。"""
    bad = set(df[TARGET_COL].unique()) - TARGET_VALUES
    if bad:
        raise DataValidationError(f"{TARGET_COL} 含非法取值:{bad}")


def summarize(df: pd.DataFrame) -> dict:
    """概览统计:行数、列数、各列类型(供数据分析页使用)。"""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
    }
