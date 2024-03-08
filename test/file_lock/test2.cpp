#include <iostream>
#include <fstream>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

int main() {
    const char *file_path = "test_file.txt";
    int count = 0; // 记录写入次数

    while (count < 10) {
        int fd = open(file_path, O_WRONLY | O_APPEND);
        if (fd < 0) {
            std::cerr << "C++: Failed to open file" << std::endl;
            return 1;
        }

        // 尝试获取文件锁
        struct flock fl;
        fl.l_type = F_WRLCK;
        fl.l_whence = SEEK_END;
        fl.l_start = 0;
        fl.l_len = 0;

        if (fcntl(fd, F_SETLK, &fl) == -1) {
            if (errno == EACCES || errno == EAGAIN) {
                // 如果文件已被锁定，则等待
                close(fd);
                sleep(1);
                continue;
            } else {
                std::cerr << "C++: Failed to acquire lock" << std::endl;
                close(fd);
                return 1;
            }
        }

        // 写入内容
        if (write(fd, "test2\n", 6) == 6) {
            count++;
            std::cout << "C++: wrote 'test2' " << count << " times" << std::endl;
        }

        // 解锁文件
        fl.l_type = F_UNLCK;
        fcntl(fd, F_SETLK, &fl);

        // 关闭文件
        close(fd);

        // 等待一下，给另一个程序一些时间来获取锁
        sleep(1);
    }

    return 0;
}

