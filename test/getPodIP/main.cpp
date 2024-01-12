#include <iostream>
#include <k8s-client-cpp/client.h>

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <namespace> <service-name>" << std::endl;
        return 1;
    }

    std::string namespaceName = argv[1];
    std::string serviceName = argv[2];

    try {
        // 创建 Kubernetes 客户端实例
        k8s::Client k8sClient;

        // 获取 headless service 关联的所有 Pods
        auto pods = k8sClient.getPods(namespaceName, [serviceName](const k8s::Pod& pod) {
            return pod.isAssociatedWithService(serviceName);
        });

        // 打印所有相关 Pod 的 IP 地址
        for (const auto& pod : pods) {
            std::cout << "Pod Name: " << pod.getName() << ", IP: " << pod.getIp() << std::endl;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
