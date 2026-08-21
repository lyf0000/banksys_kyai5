# PROGRESS · 项目进度 〔本项目活记忆 · AI 维护〕

> 时间倒序、简洁、可接力。记录:当前状态(六步流程第几步)、已完成、下一步 TODO、ADR、GOTCHAS。

---

## 当前状态(对应 06 六步流程)

**第⑥步 完成 —— 完整 CI/CD 链路首次跑通:部署成功,主机端口 8888,健康检查 ok。下一步:US-2~US-6 功能开发(分支2/3/4)。**

---

## 已完成

- 2026-08-21:初始化 `standards/00-project-context.md`、`01-requirements.md`、本文件;已读数据确认结构(train 22,500 行含 `subscribe`;test 7,500 行无标签)。
- 2026-08-21:T1 建仓完成。开源仓库 https://github.com/lyf0000/banksys_kyai5 ;main 仅引导提交 `cbdf5f8`;`data/` 与「需求」草稿留待 feature 分支提交。
- 2026-08-21:T2 确认门1 通过:人工已配置 `SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`。
- 2026-08-21:PR #2(US-1 工程化)开发完成:依赖拆分、ruff/pytest 配置、最小 app.py、Dockerfile、ci.yml、cd.yml、数据入库;本地 ruff/pytest 全绿,真跑 streamlit 健康检查 ok。
- 2026-08-21:PR #2 由人工合并(注意:合并时 CI 红,快照为修复前 head → main 缺 pytest pythonpath 修复,见 GOTCHAS)。
- 2026-08-21:CD 第一次失败:`docker: command not found`(exit 127)。
- 2026-08-21:PR #4 修复 cd.yml PATH + 带回 pythonpath 修复,CI 全绿,由人工合并。
- 2026-08-21:CD 第二次失败:补全 PATH 后 `command -v docker` 仍找不到 → 确认服务器常见路径无 docker,需人工安装。
- 2026-08-21:PR #7 合并:cd.yml 加 `workflow_dispatch` + docker 探测诊断(find 输出)。
- 2026-08-21:CD 第三次失败:服务器 docker 已装(29.1.3),但 daemon 配置的镜像加速器(USTC/网易163)均已停服,拉基础镜像 DNS 失败。
- 2026-08-21:人工换源后,CD 第四次(workflow_dispatch)成功:**部署到主机端口 8888,`/_stcore/health` 返回 ok,`http://<服务器IP>:8888`**。

---

## 下一步 TODO(第一批)

- [x] **T1 建仓**:`gh repo create banksys_kyai5 --public`,引导提交 `.gitignore` + 占位 README
- [x] **T2 ✋确认门1**:提示人工配置 Secrets,确认后再继续
- [x] **T3 ✋确认门2**:从最新 main 开 feature 分支,报分支名
- [x] **T4 本地环境**:kyai5 conda 环境(py3.11)+ 依赖(清华源)
- [x] **US-1 工程化**:PR #2 已合并(CI 红合并的教训见 GOTCHAS);PR #4/#7 修复已合并
- [x] **CD 部署链路**:服务器装 docker + 换镜像加速器后,workflow_dispatch 部署成功(端口 8888,健康检查 ok)✋确认门6
- [ ] **US-2~US-4(分支2)**:数据加载 / 预处理 / 模型训练 + `train.py --quick --assert-auc` + CI 接入模型门禁
- [ ] **US-5(分支3)**:数据分析页
- [ ] **US-6(分支4)**:在线预测页

---

## ADR(架构决策记录)

- **扁平布局 `banksys/` 而非 `src/banksys/`**(2026-08-21):Streamlit 教学项目免去 `pip install -e .` 步骤,import 零配置;已同步更新 00 目录地图。
- **模型训练放在 Docker build 内**(2026-08-21):镜像自带模型,部署即含推理能力;本地/CI 用 `train.py --quick` 快速门禁,完整训练由 CI 的 docker build 兜底(US-4 接入)。
- **数据进 Git**(2026-08-21):公开脱敏教学数据(~3.7MB),保证 CI/CD 干净 runner 可复现;模型产物 models/ 不进 Git。

---

## GOTCHAS(踩坑记录)

- **Linux CI 上 `import banksys` 失败**(2026-08-21):本地 `python -m pytest` 会把 cwd 加入 `sys.path` 掩盖问题,CI 直接跑 `pytest` 时项目根不在 `sys.path`。修复:`pyproject.toml` 加 `pythonpath = ["."]`。
- **CD `docker: command not found`(exit 127)**(2026-08-21):appleboy/ssh-action 非交互 shell 的 PATH 很小。修复:cd.yml 部署脚本开头补全 PATH 并加存在性检查。**但补全后仍找不到 → 服务器本身无 docker 或装在非标准位置,需人工在服务器确认**(第二次 CD 失败,2026-08-21)。
- **CI 红时合并 PR**(2026-08-21):PR #2 在 CI 红时被合并,且合并快照为修复前 head,导致 main 缺修复。提醒:合并前必须确认 PR checks 全绿(分支保护可强制,可选开启)。
- **github.com 网络抖动**(2026-08-21):git fetch/push 偶发 Connection reset / 443 超时,重试或稍等恢复;期间可离线切分支、写代码,恢复后 rebase 推送。
- **服务器 docker 镜像加速器失效**(2026-08-21):daemon.json 里 USTC(`docker.mirrors.ustc.edu.cn`)与网易(`hub-mirror.c.163.com`)均停服,拉镜像报 `no such host`。修复:换可用源(如 `docker.1ms.run` / `docker.m.daocloud.io`)后 `systemctl restart docker`。判断是否命中:报错域名出现在 docker pull 的 Head 请求里。
