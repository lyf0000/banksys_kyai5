# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的"身份档案"。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。

---

## 1. 项目是什么

- **项目名称**:`banksys_kyai5`(开源仓库;Docker 镜像名与容器名同为此值)
- **一句话目标**:基于银行营销数据构建 Web 应用,提供「交互式数据分析」与「离线训练模型 + 在线认购预测」两大功能。
- **使用者/受益者**:银行营销业务人员、课程教学演示与开源社区学习者。
- **核心功能**:
  - **数据分析交互页**:数据概览、目标分布、交互式可视化、筛选联动。
  - **离线训练 + 在线预测**:基于 `train.csv` 离线训练模型;用户以点选表单输入客户特征,得到「是否认购」预测及概率。
- **输入/数据**:
  - `data/train.csv`:22,500 行 × 21 列,含目标列 `subscribe`(yes/no)。
  - `data/test.csv`:7,500 行 × 20 列,无目标列(保留作演示/扩展用,训练不使用)。
  - 公开脱敏教学数据(类 UCI Bank Marketing),**进 Git**——保证 CI/CD 在干净 runner 上可复现;模型产物**不进 Git**。

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 课程指定 |
| Web 框架 | Streamlit | 交互式图表 + 点选表单开发效率高;自带 `/_stcore/health` 健康检查端点 |
| 数据处理/建模 | pandas + scikit-learn | 经典表格二分类,依赖少、训练快、易复现 |
| 测试 | pytest | 课程指定;页面用 Streamlit `AppTest` 冒烟测试 |
| 格式/静态检查 | ruff | 课程指定,一个工具管 format + lint |
| 打包/运行 | Docker | 镜像名/容器名 `banksys_kyai5`;构建时训练模型,镜像自带模型 |
| CI/CD | GitHub Actions | 通用、可视化;PR 触发 CI,合并 main 触发 CD |

## 3. 目录地图

```text
banksys_kyai5/
├── standards/                 # AI 项目记忆与通用规范
├── data/                      # train.csv / test.csv(公开脱敏教学数据,进 Git)
├── src/banksys/               # 核心包:data.py 加载校验 / preprocess.py 编码 / model.py 训练推理
├── scripts/
│   └── train.py               # 离线训练入口(--quick 快速门禁 / --assert-auc 阈值断言)
├── app.py                     # Streamlit 入口 = 数据分析页
├── pages/
│   └── 1_prediction.py        # 在线预测页(点选表单)
├── models/                    # 训练产物(不进 Git;Docker build 时生成)
├── tests/                     # pytest 单元测试 + AppTest 页面冒烟测试
├── requirements.txt           # 生产运行依赖
├── requirements-dev.txt       # 本地/CI 检查依赖(pytest/ruff/coverage)
├── Dockerfile                 # 构建时执行完整训练 + AUC 断言
├── .github/workflows/
│   ├── ci.yml                 # PR:ruff / pytest+覆盖率 / 模型快速门禁 / docker build
│   └── cd.yml                 # main:SSH 部署 + 健康检查
├── .gitignore
└── README.md
```

> 新增目录前先更新本节,避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest --cov=src --cov-fail-under=80`(核心包 src/ 覆盖率 ≥ 80%;页面用 AppTest 冒烟) |
| 覆盖率 | ≥ 80%(src/ 包) |
| 构建 | `docker build`(CI/CD 执行,本地不强制) |
| 模型指标门禁 | 本地/CI:`python scripts/train.py --quick --assert-auc 0.60`;完整数据训练 + 同断言在 Docker build 内执行,不达标构建失败 |
| 健康检查 | `curl -fsS http://localhost:<PORT>/_stcore/health` 返回 `ok` |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- 数据:`data/` **进 Git**(公开脱敏教学数据);`models/`、缓存、虚拟环境不进 Git。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。
- 训练固定 `random_state=42`,保证可复现、CI 不 flaky。

## 6. 部署/CI 占位符取值

> `guides/` 和 workflow 里的通用占位符,在本项目里的真实值只写这里。

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `banksys_kyai5` | 镜像名/容器名/仓库名 |
| `<DEPLOY_DIR>` | `/opt/banksys_kyai5` | 服务器部署目录 |
| `<PORT>` | `8888` | 容器内固定 8888;主机端口 8888 优先,回退区间 8888-8898 |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `/_stcore/health` | Streamlit 自带健康检查 |
| `<SSH_USER>` | 待定 | 部署时由用户提供 |
| `<SSH_HOST>` | 待定 | 部署时由用户提供,不写密钥 |
