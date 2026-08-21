# PROGRESS · 项目进度 〔本项目活记忆 · AI 维护〕

> 时间倒序、简洁、可接力。记录:当前状态(六步流程第几步)、已完成、下一步 TODO、ADR、GOTCHAS。

---

## 当前状态(对应 06 六步流程)

**第②步 —— 分支已开,✋确认门2:等待确认后进入模块开发。**

---

## 已完成

- 2026-08-21:初始化 `standards/00-project-context.md`、`01-requirements.md`、本文件;已读数据确认结构(train 22,500 行含 `subscribe`;test 7,500 行无标签)。
- 2026-08-21:T1 建仓完成。开源仓库 https://github.com/lyf0000/banksys_kyai5 ;main 仅引导提交 `cbdf5f8`(.gitignore + 占位 README + standards/);`data/` 与「需求」草稿留待 feature 分支提交。
- 2026-08-21:T2 确认门1 通过:人工已配置 `SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`(gh secret list 核对无误)。
- 2026-08-21:T3 分支已开:创建 Issue #1(US-1 工程化),切出 `feature/1-project-init`。

---

## 下一步 TODO(第一批)

- [x] **T1 建仓**:`gh repo create banksys_kyai5 --public`,引导提交 `.gitignore` + 占位 README(不在 main 上做真实开发)
- [x] **T2 ✋确认门1**:提示人工配置 Secrets `SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`,确认后再继续
- [ ] **T3 ✋确认门2**:从最新 main 开 feature 分支(如 `feature/1-project-init`),报分支名
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

_暂无(按 06 故障反哺铁律,真实故障必须写回)。_
