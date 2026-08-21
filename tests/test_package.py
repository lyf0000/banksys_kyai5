"""banksys 包元信息测试。"""

from banksys import APP_NAME, VERSION


def test_app_name_matches_repo():
    # 仓库、镜像、容器同名,由 00-project-context 固定
    assert APP_NAME == "banksys_kyai5"


def test_version_is_semver():
    major, minor, patch = VERSION.split(".")
    assert all(part.isdigit() for part in (major, minor, patch))
