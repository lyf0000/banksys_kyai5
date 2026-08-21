# banksys_kyai5

基于银行营销数据(公开脱敏教学数据)的 Streamlit Web 应用,两大功能:

1. **数据分析交互页**(主页):数据概览、认购目标分布、交互式可视化(年龄分布/类别认购率/数值分箱认购率)与筛选联动。
2. **在线认购预测**(`pages/1_prediction.py`):离线训练模型后,通过点选表单输入客户特征,预测其是否认购定期存款(含置信度)。

## 数据

| 文件 | 规模 | 说明 |
|---|---|---|
| `data/train.csv` | 22,500 行 × 22 列 | id + 20 特征 + 目标列 `subscribe`(yes/no) |
| `data/test.csv` | 7,500 行 × 21 列 | id + 20 特征,无目标列,留作演示/扩展 |

公开脱敏教学数据(类 UCI Bank Marketing),进 Git 以保证 CI/CD 可复现。

## 本地运行

```bash
# 环境:conda + Python 3.11
conda create -y -n kyai5 python=3.11 && conda activate kyai5

# 依赖(国内可用清华源)
pip install -r requirements.txt -r requirements-dev.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 离线训练模型(预测页依赖 models/ 产物)
python scripts/train.py          # 完整训练,输出 models/model.joblib 等
# python scripts/train.py --quick --assert-auc 0.60   # 快速门禁版

# 启动应用(端口 8888)
streamlit run app.py --server.port 8888
```

## 质量门禁

```bash
ruff format --check .   # 格式检查
ruff check .            # 静态检查
pytest                  # 单元测试 + 覆盖率(≥ 80%,核心包 banksys/)
python scripts/train.py --quick --assert-auc 0.60   # 模型快速门禁(AUC 底线)
```

## Docker

```bash
docker build -t banksys_kyai5 .   # 构建时训练完整模型并断言 AUC,镜像自带模型
docker run -d --name banksys_kyai5 -p 8888:8888 banksys_kyai5
curl http://localhost:8888/_stcore/health   # 返回 ok
```

## CI/CD

- **CI**(PR 触发):格式检查、静态检查、单元测试 + 覆盖率、模型快速门禁、`docker build`(含完整训练 + AUC 断言)。
- **CD**(合并 main 触发,亦可手动 `workflow_dispatch`):同步代码到服务器 → 构建镜像 → 幂等部署容器 `banksys_kyai5`(容器内 8888,主机端口 8888 优先、8888-8898 回退)→ 健康检查 `/_stcore/health`。
- 部署需要 GitHub Secrets:`SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`(见 `standards/05-cicd-standards.md` 第 5 节)。

## 项目规范

工程规范、需求(用户故事 + 验收标准)与进度见 `standards/` 目录;开发按六步交付流程走 feature 分支 + PR,CI 红灯不合并,合并由人工执行。
