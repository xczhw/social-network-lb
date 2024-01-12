# 使用带有 C++ 编译器的基础镜像
FROM ubuntu:latest

# 安装必要的软件包
RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    git \
    libcurl4-openssl-dev \
    libssl-dev

# 克隆 k8s-client-cpp 仓库
RUN git clone https://github.com/yglukhov/k8s-client-cpp.git

# 构建 k8s-client-cpp 库
RUN cd k8s-client-cpp && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make && \
    make install

# 将您的 C++ 源代码添加到容器中
WORKDIR /usr/src/myapp
COPY . /usr/src/myapp

# 编译您的程序
RUN g++ -o myprogram main.cpp -l k8s-client-cpp

# 运行程序
CMD ["./myprogram"]
