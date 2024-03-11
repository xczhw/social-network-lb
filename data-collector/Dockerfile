# 使用官方Python运行时作为父镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /usr/src/app

# 将当前目录内容复制到容器中的工作目录
COPY . .

# 安装main.py所需的所有依赖
RUN pip install --no-cache-dir flask

# 使端口8080可用于世界之外的通信
EXPOSE 8080

# 定义环境变量
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# 在容器启动时运行main.py
CMD ["flask", "run", "--port=8080"]
