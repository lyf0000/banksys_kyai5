"""Streamlit 数据分析页 AppTest 冒烟测试(US-5)。"""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from banksys import APP_NAME

# AppTest.from_file 的相对路径按测试文件目录解析,这里定位到项目根
APP_ENTRY = Path(__file__).resolve().parent.parent / "app.py"


def test_app_renders_without_exception():
    # Arrange
    at = AppTest.from_file(str(APP_ENTRY), default_timeout=60)

    # Act
    at.run()

    # Assert
    assert not at.exception
    assert at.title[0].value == APP_NAME


def test_app_shows_overview_metrics():
    at = AppTest.from_file(str(APP_ENTRY), default_timeout=60).run()

    # 客户数 / 特征数 / 认购率 三个指标
    assert len(at.metric) == 3
    assert at.metric[0].value == "22,500"
    assert at.metric[2].value == "13.1%"


def test_app_filters_update_charts():
    at = AppTest.from_file(str(APP_ENTRY), default_timeout=60).run()

    # 侧边栏筛选器存在(4 个 selectbox)
    assert len(at.sidebar.selectbox) >= 4

    # 选择职业 admin. 后重跑,不应崩溃
    at.sidebar.selectbox[0].select("admin.")
    at.run()
    assert not at.exception


def test_app_charts_render():
    at = AppTest.from_file(str(APP_ENTRY), default_timeout=60).run()

    assert not at.exception
    # 1 个目标分布 + 3 个交互可视化
    assert len(at.get("vega_lite_chart")) >= 4
