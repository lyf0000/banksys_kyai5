# 01 · 需求 / 活 PRD 〔本项目活记忆 · AI 维护〕

> **作用**:这是本项目唯一的需求文档。所有新功能、缺陷、技术债都追加到这里,不要另起多个 PRD 文件。
> **更新时机**:每次有新需求、需求变更、验收标准变化时更新。

---

## 1. 需求来源

| 类型 | 来源 | 进入方式 |
|---|---|---|
| 功能需求 Feature | 用户 / 老师 / 产品 / 客户 | 写成用户故事 |
| 缺陷 Bug | 测试 / 线上日志 / 用户反馈 | 写复现步骤和期望结果 |
| 技术债 Tech Debt | 开发 / Review / CI/CD 故障 | 写影响和修复目标 |

---

## 2. Issue 生命周期

| 阶段 | 状态 | 动作 |
|---|---|---|
| 提出 | Open | 写清场景、目标、验收标准 |
| 排期 | Backlog / Todo | 决定优先级和负责人 |
| 开发 | In Progress | 从 main 开 feature 分支 |
| 评审 | In Review | 提 PR,等待 CI 和 Review |
| 合并 | Done | PR 合并 main,自动关闭 Issue |
| 验收 | Verified | 按验收标准确认 |

**追踪规则**:分支名带 Issue 号,PR 描述写 `closes #<编号>`。

---

## 3. 用户故事模板

```text
### US-<编号> <一句话标题> · 状态: Backlog
作为 <角色>,
我想要 <能力>,
以便 <价值>。

验收标准:
- AC1: Given <前提>,When <动作>,Then <可验证结果>。
- AC2: <补充标准>

技术备注:
- <可选:约束、边界、风险>
```

---

## 4. 需求清单

### US-1 初始化项目工程化与 CI/CD · 状态: Backlog

作为 **项目开发者**,
我想要 项目具备基础工程结构、依赖拆分、Docker 与完整 CI/CD,
以便 每次开发自动检查、合并 main 后自动部署上线。

验收标准:
- AC1: Given 全新开源仓库 `banksys_kyai5`,When 从 main 开 feature 分支完成工程化初始化,Then 不直接 push main。
- AC2: Given 发起 PR,When CI 运行,Then 依次通过 `ruff format --check .`、`ruff check .`、`pytest --cov=src --cov-fail-under=80`、模型快速门禁(`scripts/train.py --quick --assert-auc 0.60`)、`docker build`,全部成功。
- AC3: Given CI 全绿,When 人工 Review 通过并合并 main,Then 默认保留分支。
- AC4: Given 合并 main,When CD 触发,Then 服务器上构建镜像(构建时训练完整模型并断言 AUC)、以容器名 `banksys_kyai5` 幂等部署(容器内端口 8888,主机端口 8888 优先、8888-8898 回退),最终 `curl /_stcore/health` 返回 `ok` 并打印访问地址。
- AC5: Given 开源仓库,When 访问者阅读 README,Then 可按文档完成本地环境搭建、训练、运行、测试与部署全流程。
- AC6: Given 每一步完成,When 更新 `standards/PROGRESS.md`,Then 记录状态、命令结果与踩坑。

### US-2 数据加载与校验模块 · 状态: Backlog

作为 **项目开发者**,
我想要 统一的数据加载与校验函数,
以便 训练与页面共用同一数据口径,并尽早暴露脏数据。

验收标准:
- AC1: Given `data/train.csv`,When 调用加载函数,Then 返回 21 列 DataFrame 且 `subscribe` 取值只含 yes/no。
- AC2: Given `data/test.csv`,When 调用加载函数,Then 返回 20 列(无 `subscribe`)。
- AC3: Given 数据文件缺失或列名不符,When 调用加载函数,Then 抛出含明确信息的异常,不做静默降级。
- AC4: Given 合法数据,When 校验函数运行,Then 输出行数、各列类型;类别列中的 `unknown` 视为合法取值。

### US-3 特征预处理模块 · 状态: Backlog

作为 **项目开发者**,
我想要 可复用的特征预处理管线,
以便 离线训练与在线预测使用完全一致的特征编码。

验收标准:
- AC1: Given 训练数据,When 执行 `fit_transform`,Then 类别特征被编码为数值,输出特征矩阵,且编码器状态可保存复用。
- AC2: Given 已 fit 的编码器,When 对单条用户输入执行 `transform`,Then 产生与训练一致的编码(含训练数据中出现的 `unknown` 取值)。
- AC3: Given 异常输入(缺失、越界),When 执行预处理,Then 给出可定位的错误信息,页面不崩溃。

### US-4 离线训练与模型门禁 · 状态: Backlog

作为 **数据科学开发者**,
我想要 可复现的离线训练脚本与模型产物,
以便 页面加载模型即可预测,CI/CD 能守住模型质量底线。

验收标准:
- AC1: Given 完整 `train.csv` 与固定 `random_state=42`,When 运行 `scripts/train.py`,Then 产出 `models/` 下模型文件与 `metrics.json`(含 AUC、准确率),重复运行结果一致。
- AC2: Given `--quick` 模式(固定种子子样本),When 本地/CI 运行,Then 数分钟内完成,可作为快速质量门禁。
- AC3: Given `--assert-auc 0.60`,When 验证集 AUC 低于阈值,Then 脚本以非 0 退出码失败,CI 红灯。
- AC4: Given 已保存的模型,When 调用推理接口传入特征 dict,Then 返回 `subscribe` 类别与概率,口径与训练时一致。

技术备注:
- 选型 `sklearn.ensemble.RandomForestClassifier`,固定 `random_state=42`;类别编码用 `OrdinalEncoder`(保留 `unknown`)。
- 完整训练在 Docker build 内执行,镜像自带模型;本地/CI 用 `--quick` 快速门禁。
- `duration` 是通话时长,真实业务中预测时点未知,课程演示保留为用户可输入特征。

### US-5 数据分析交互页 · 状态: Backlog

作为 **银行营销业务人员**,
我想要 一个交互式数据分析页面,
以便 快速了解客户数据全貌与认购分布。

验收标准:
- AC1: Given 打开应用主页,When 页面加载,Then 显示数据概览:行数、列数、各列类型与缺失情况。
- AC2: Given 页面加载,Then 显示 `subscribe` 目标分布(计数与占比)。
- AC3: Given 页面加载,Then 提供至少 3 种交互式可视化:数值特征分布(如 `age`)、按 `subscribe` 分组的类别特征对比(如 `job`/`education`)、社会经济指标(如 `emp_var_rate`/`lending_rate3m`)与认购率关系。
- AC4: Given 用户调整筛选控件(如职业/月份/教育),When 筛选生效,Then 统计与图表联动更新。
- AC5: Given 页面,When 运行 Streamlit `AppTest` 冒烟测试,Then 渲染无异常、无崩溃。

### US-6 在线预测页 · 状态: Backlog

作为 **银行营销业务人员**,
我想要 通过点选表单输入客户特征,
以便 立即得到该客户是否会认购定期存款的预测及置信度。

验收标准:
- AC1: Given 打开预测页,When 页面渲染,Then 提供全部训练特征的录入控件:类别特征用下拉/单选(选项与训练数据一致,含 `unknown`),数值特征用数字输入,均有合理默认值。
- AC2: Given 用户填写并提交,When 模型已加载,Then 显示「预测:认购/不认购」及概率(阈值 0.5)。
- AC3: Given 非法输入(如负年龄),When 提交,Then 页面给出校验提示且不崩溃。
- AC4: Given 模型文件不存在,When 打开预测页,Then 显示友好提示引导先运行训练,而非堆栈错误。
- AC5: Given 一条训练样本,When 走「页面输入 → 预测」链路,Then 端到端测试通过,页面预测与模型推理接口结果一致。

---

## 5. 非功能需求

- **安全**:密钥只进 Secrets,不进 Git。
- **可维护**:一需求一小 PR,避免大爆炸式提交。
- **可测试**:核心逻辑必须有单元测试;页面有 AppTest 冒烟测试。
- **可部署**:部署后必须有健康检查或等价验证。
- **可复现**:训练固定随机种子,依赖版本在 requirements 中固定。
- **性能**:单次预测 < 1 秒;完整训练在镜像构建中可接受时间内完成。
