# banksys_kyai5

基于银行营销数据(公开脱敏教学数据)的 Streamlit Web 应用,两大功能:

1. **数据分析交互页**:数据概览、目标分布、交互式可视化与筛选联动。
2. **在线认购预测**:离线训练模型后,通过点选表单输入客户特征,预测其是否认购定期存款。

> 迭代开发中:工程化骨架已就位,数据分析页与在线预测页按 `standards/01-requirements.md` 的 US-2~US-6 逐 PR 交付。

## 数据

| 文件 | 规模 | 说明 |
|---|---|---|
| `data/train.csv` | 22,500 行 × 21 列 | 含目标列 `subscribe`(yes/no) |
| `data/test.csv` | 7,500 行 × 20 列 | 无目标列,留作演示/扩展 |

公开脱敏教学数据(类 UCI Bank Marketing),进 Git 以保证 CI/CD 可复现。

## 本地运行

```bash
# 环境:conda + Python 3.11(本项目使用 kyai5 环境)
conda create -y -n kyai5 python=3.11 && conda activate kyai5

# 依赖(国内可用清华源)
pip install -r requirements.txt -r requirements-dev.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 启动应用(端口 8888)
streamlit run app.py --server.port 8888
```

## 质量门禁

```bash
ruff format --check .   # 格式检查
ruff check .            # 静态检查
pytest                  # 单元测试 + 覆盖率(≥ 80%,核心包 banksys/)
# 模型快速门禁(US-4 接入后):python scripts/train.py --quick --assert-auc 0.60
```

## Docker

```bash
docker build -t banksys_kyai5 .
docker run -d --name banksys_kyai5 -p 8888:8888 banksys_kyai5
curl http://localhost:8888/_stcore/health   # 返回 ok
```

镜像构建时执行完整模型训练并断言 AUC(US-4 接入后),镜像自带模型。

## CI/CD

- **CI**(PR 触发):格式检查、静态检查、单元测试 + 覆盖率、模型快速门禁(US-4 接入后)、`docker build`。
- **CD**(合并 main 触发):同步代码到服务器 → 构建镜像 → 幂等部署容器 `banksys_kyai5`(容器内 8888,主机端口 8888 优先、8888-8898 回退)→ 健康检查 `/_stcore/health`。
- 部署需要 GitHub Secrets:`SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`(见 `standards/05-cicd-standards.md` 第 5 节)。

## 项目规范

工程规范、需求(用户故事 + 验收标准)与进度见 `standards/` 目录;开发按六步交付流程走 feature 分支 + PR,CI 红灯不合并,合并由人工执行。
