"""数据加载与校验测试(US-2)。"""

import pytest

from banksys.data import (
    CATEGORICAL_COLS,
    DATA_DIR,
    FEATURE_COLS,
    NUMERIC_COLS,
    TARGET_COL,
    DataValidationError,
    load_data,
    summarize,
    validate_train_target,
)


def test_feature_cols_cover_all_21_train_columns():
    # 特征顺序固定:类别 10 + 数值 10;训练集另有 id 与 subscribe
    assert len(CATEGORICAL_COLS) == 10
    assert len(NUMERIC_COLS) == 10
    assert len(FEATURE_COLS) == 20
    assert len(set(FEATURE_COLS)) == 20


def test_load_train_has_expected_shape_and_target():
    df = load_data("train")

    # 22 列 = id + 20 特征 + subscribe(顺序不敏感,集合校验)
    assert df.shape == (22500, 22)
    assert set(df.columns) == {"id"} | set(FEATURE_COLS) | {TARGET_COL}


def test_load_test_has_no_target():
    df = load_data("test")

    # 21 列 = id + 20 特征,无 subscribe
    assert df.shape == (7500, 21)
    assert TARGET_COL not in df.columns


def test_validate_train_target_accepts_yes_no():
    df = load_data("train")
    validate_train_target(df)  # 不抛异常即通过


def test_validate_train_target_rejects_bad_value():
    df = load_data("train")
    df.iloc[0, df.columns.get_loc(TARGET_COL)] = "maybe"

    with pytest.raises(DataValidationError, match="maybe"):
        validate_train_target(df)


def test_load_data_missing_file_raises(tmp_path, monkeypatch):
    monkeypatch.setattr("banksys.data.DATA_DIR", tmp_path)

    with pytest.raises(DataValidationError, match="数据文件不存在"):
        load_data("train")


def test_load_data_wrong_columns_raises(tmp_path, monkeypatch):
    monkeypatch.setattr("banksys.data.DATA_DIR", tmp_path)
    (tmp_path / "train.csv").write_text("id,age\n1,30\n", encoding="utf-8")

    with pytest.raises(DataValidationError, match="列名不符"):
        load_data("train")


def test_load_data_rejects_unknown_kind():
    with pytest.raises(ValueError, match="train"):
        load_data("prediction")


def test_summarize_reports_rows_and_dtypes():
    df = load_data("train")
    info = summarize(df)

    assert info["rows"] == 22500
    assert info["columns"] == 22
    assert len(info["dtypes"]) == 22


def test_data_dir_points_at_repo_data():
    assert (DATA_DIR / "train.csv").exists()
    assert (DATA_DIR / "test.csv").exists()
