"""训练脚本门禁测试(US-4):--quick 模式 + AUC 断言。"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAIN_SCRIPT = REPO_ROOT / "scripts" / "train.py"


def run_train(*args: str, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TRAIN_SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO_ROOT,
    )


def test_quick_train_passes_low_auc_gate(tmp_path):
    result = run_train("--quick", "--assert-auc", "0.5", "--out-dir", str(tmp_path))

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "model.joblib").exists()
    assert (tmp_path / "preprocessor.joblib").exists()
    assert (tmp_path / "metrics.json").exists()


def test_auc_gate_fails_below_threshold(tmp_path):
    # 0.999 必然达不到,验证门禁以非 0 退出码失败
    result = run_train("--quick", "--assert-auc", "0.999", "--out-dir", str(tmp_path))

    assert result.returncode == 1
    assert "AUC gate failed" in result.stdout
