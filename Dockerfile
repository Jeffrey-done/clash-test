FROM python:3.10-slim

WORKDIR /app

# 复制必要文件
COPY requirements.txt .
COPY *.py .
COPY config.yaml .
COPY utils/ ./utils/
COPY templates/ ./templates/
COPY static/ ./static/

# 创建必要的目录
RUN mkdir -p output local_configs

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn gevent

# 暴露端口
EXPOSE 8080

# 使用 Gunicorn 作为生产环境服务器
CMD ["gunicorn", "-c", "gunicorn_config.py", "webui:app"] 