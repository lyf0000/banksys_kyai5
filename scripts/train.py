"""离线训练入口(US-4)。

完整训练(默认):全量 train.csv,300 棵树,由 Docker build 调用。
快速门禁(--quick):子样本 + 100 棵树,本地/CI 数分钟内完成。
AUC 门禁(--assert-auc):验证集 AUC 低于阈值时以非 0 退出码失败。
"""

import argparse
import sys
from pathlib import Path

from sklearn.model_selection import train_test_split

# 直接以 python scripts/train.py 运行时,项目根不在 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from banksys.data import TARGET_COL, load_data, validate_train_target  # noqa: E402
from banksys.model import (
    DEFAULT_TREES,
    MODEL_DIR,
    QUICK_TREES,
    build_model,
    evaluate,
    save_pipeline,
)
from banksys.preprocess import fit_preprocessor, transform_features

QUICK_SAMPLE_SIZE = 5000
TEST_SIZE = 0.2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true", help="子样本快速训练,用于本地/CI 门禁")
    parser.add_argument(
        "--assert-auc",
        type=float,
        default=None,
        help="验证集 AUC 低于该阈值时以退出码 1 失败",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=MODEL_DIR,
        help=f"产物输出目录(默认 {MODEL_DIR})",
    )
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    df = load_data("train")
    validate_train_target(df)

    if args.quick:
        df = df.sample(n=QUICK_SAMPLE_SIZE, random_state=args.seed)
        trees = QUICK_TREES
    else:
        trees = DEFAULT_TREES

    y = (df[TARGET_COL] == "yes").astype(int)
    preprocessor = fit_preprocessor(df)
    X = transform_features(preprocessor, df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=args.seed,
    )

    model = build_model(n_estimators=trees)
    model.fit(X_train, y_train)
    metrics = evaluate(model, X_test, y_test)

    print(f"training done: {len(df)} rows, {trees} trees")
    print(f"AUC={metrics['auc']:.4f}  Accuracy={metrics['accuracy']:.4f}")

    if args.assert_auc is not None and metrics["auc"] < args.assert_auc:
        print(f"AUC gate failed: {metrics['auc']:.4f} < {args.assert_auc}")
        return 1

    save_pipeline(model, preprocessor, metrics, out_dir=args.out_dir)
    print(f"artifacts saved: {args.out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
