"""在线预测页 AppTest 冒烟测试(US-6)。"""

import subprocess
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).resolve().parent.parent
PAGE_ENTRY = REPO_ROOT / "pages" / "1_prediction.py"


@pytest.fixture(scope="module")
def trained_artifacts():
    """页面需要 models/ 产物:先跑一次 quick 训练生成。"""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "train.py"), "--quick"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr
    yield
    # 产物保留在本地 models/(已被 .gitignore),不清理


def _run_app():
    return AppTest.from_file(str(PAGE_ENTRY), default_timeout=60).run()


def test_prediction_page_renders(trained_artifacts):
    at = _run_app()

    assert not at.exception
    assert at.title[0].value == "在线认购预测"


def test_prediction_form_has_all_feature_controls(trained_artifacts):
    at = _run_app()

    # 10 个类别下拉 + 10 个数值输入
    assert len(at.selectbox) >= 10
    assert len(at.number_input) >= 10


def test_default_submit_returns_result(trained_artifacts):
    at = _run_app()

    at.button[0].click()
    at.run()

    assert not at.exception
    # 提交后应出现 成功/警示 结果之一
    assert len(at.success) + len(at.warning) == 1
