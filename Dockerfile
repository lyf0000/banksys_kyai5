# 镜像名固定 banksys_kyai5;容器内端口固定 8888,主机端口 8888 优先、8888-8898 回退
# 注意:slim 基础镜像无 curl,HEALTHCHECK 用 python urllib 实现
FROM python:3.11-slim

ARG PIP_INDEX_URL=https://pypi.org/simple

WORKDIR /app

# 先装依赖再复制代码,利用 Docker 层缓存
COPY requirements.txt ./
RUN pip install --no-cache-dir --timeout 120 -i "${PIP_INDEX_URL}" -r requirements.txt

COPY . .

# 构建时训练完整模型并断言 AUC(US-4):AUC 不达标则构建失败,镜像自带模型
RUN python scripts/train.py --assert-auc 0.60

EXPOSE 8888

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8888/_stcore/health', timeout=4)" || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8888", "--server.address=0.0.0.0", "--server.headless=true"]
