# PROGRESS · 项目进度 〔本项目活记忆 · AI 维护〕

> 时间倒序、简洁、可接力。记录:当前状态(六步流程第几步)、已完成、下一步 TODO、ADR、GOTCHAS。

---

## 当前状态(对应 06 六步流程)

**第⑤步 —— PR #4 已发起、CI 全绿,✋确认门5:等待人工 Review 合并。**

---

## 已完成

- 2026-08-21:初始化 `standards/00-project-context.md`、`01-requirements.md`、本文件;已读数据确认结构(train 22,500 行含 `subscribe`;test 7,500 行无标签)。
- 2026-08-21:T1 建仓完成。开源仓库 https://github.com/lyf0000/banksys_kyai5 ;main 仅引导提交 `cbdf5f8`;`data/` 与「需求」草稿留待 feature 分支提交。
- 2026-08-21:T2 确认门1 通过:人工已配置 `SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`。
- 2026-08-21:PR #2(US-1 工程化)开发完成:依赖拆分、ruff/pytest 配置、最小 app.py、Dockerfile、ci.yml、cd.yml、数据入库;本地 ruff/pytest 全绿,真跑 streamlit 健康检查 ok。
- 2026-08-21:PR #2 由人工合并(注意:合并时 CI 红,快照为修复前 head → main 缺 pytest pythonpath 修复,见 GOTCHAS)。
- 2026-08-21:CD 首次运行失败:`docker: command not found`(exit 127)。
- 2026-08-21:开 Issue #3,fix 分支 `fix/3-cd-docker-path` 修复 cd.yml PATH + 带回 pythonpath 修复;PR #4 CI 全绿(ruff/pytest/覆盖率/docker build)。

---

## 下一步 TODO(第一批)

- [x] **T1 建仓**:`gh repo create banksys_kyai5 --public`,引导提交 `.gitignore` + 占位 README
- [x] **T2 ✋确认门1**:提示人工配置 Secrets,确认后再继续
- [x] **T3 ✋确认门2**:从最新 main 开 feature 分支,报分支名
- [ ] **T12 延续**:人工合并 PR #4 → CD 自动部署 → 汇报端口/健康检查 ✋确认门6
- [ ] **US-2~US-4(分支2)**:数据加载 / 预处理 / 模型训练 + `train.py --quick --assert-auc` + CI 接入模型门禁
- [ ] **US-5(分支3)**:数据分析页
- [ ] **US-6(分支4)**:在线预测页
- [ ] **T4 本地环境**:conda 建 `python=3.11` 环境,安装 `requirements.txt` + `requirements-dev.txt`(清华源)
- [ ] **T5 M1 数据模块**:`src/banksys/data.py` + tests(US-2)→ 汇报 ✋确认门3
- [ ] **T6 M2 预处理模块**:`src/banksys/preprocess.py` + tests(US-3)→ 汇报 ✋确认门3
- [ ] **T7 M3 模型模块**:`src/banksys/model.py` + `scripts/train.py`(`--quick` / `--assert-auc`)+ tests(US-4)→ 汇报 ✋确认门3
- [ ] **T8 M4 数据分析页**:`app.py` + AppTest 冒烟测试(US-5)→ 汇报 ✋确认门3
- [ ] **T9 M5 在线预测页**:`pages/1_prediction.py` + AppTest 冒烟测试(US-6)→ 汇报 ✋确认门3
- [ ] **T10 M6 工程化**:`Dockerfile`(构建时训练+断言 AUC)、`.github/workflows/ci.yml`、`cd.yml`、requirements 拆分(US-1)→ 汇报 ✋确认门3
- [ ] **T11 本地 CI 自检 ✋确认门4**:`ruff format --check .` + `ruff check .` + `pytest --cov=src --cov-fail-under=80` + `python scripts/train.py --quick --assert-auc 0.60`(本地不强制 docker),全绿才继续
- [ ] **T12 ✋确认门5**:push feature 分支 → `gh pr create`(closes #1)→ 报 PR 链接 + CI 状态(云端复检含 `docker build`)
- [ ] **T13 ✋确认门6**:人工 Review 合并(人操作)→ CD 自动部署 → 汇报最终端口、`/_stcore/health` 结果、访问地址

---

## ADR(架构决策记录)

_暂无(建仓开发后追加)。_

---

## GOTCHAS(踩坑记录)

- **Linux CI 上 `import banksys` 失败**(2026-08-21):本地 `python -m pytest` 会把 cwd 加入 `sys.path` 掩盖问题,CI 直接跑 `pytest` 时项目根不在 `sys.path`。修复:`pyproject.toml` 加 `pythonpath = ["."]`(pytest 官方配置)。
- **CD `docker: command not found`(exit 127)**(2026-08-21):appleboy/ssh-action 非交互 shell 的 PATH 很小,docker 若装在 `/snap/bin` 等位置会找不到。修复:cd.yml 部署脚本开头补全 PATH,并加 `command -v docker` 存在性检查给出可读报错。
- **CI 红时合并 PR**(2026-08-21):PR #2 在 CI 红时被合并,且合并快照为修复前 head,导致 main 缺修复。提醒:合并前必须确认 PR checks 全绿(分支保护可强制此约束,可选开启)。
