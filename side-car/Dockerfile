# 使用官方 Python 运行时作为基础镜像
FROM python:3.8-slim

# 在容器中设置工作目录
WORKDIR /usr/src/app

# 将当前目录内容复制到容器的 /usr/src/app
COPY . .

# 安装构建依赖项和所需包
RUN apt-get update \
    && apt-get install -y gcc python3-dev \
    && pip3 install --no-cache-dir kubernetes psutil

# 容器启动时运行脚本
CMD ["python3", "-u", "side_car.py"]