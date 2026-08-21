"""Streamlit 入口页 AppTest 冒烟测试。"""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from banksys import APP_NAME

# AppTest.from_file 的相对路径按测试文件目录解析,这里定位到项目根
APP_ENTRY = Path(__file__).resolve().parent.parent / "app.py"


def test_app_renders_without_exception():
    # Arrange
    at = AppTest.from_file(str(APP_ENTRY), default_timeout=30)

    # Act
    at.run()

    # Assert
    assert not at.exception
    assert at.title[0].value == APP_NAME
