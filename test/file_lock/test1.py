import fcntl
import time

file_path = 'test_file.txt'
count = 0  # 记录写入次数

while count < 10:
    with open(file_path, 'a') as lock_file:
        try:
            # 尝试获取文件锁
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # 写入内容
            lock_file.write('test1\n')
            lock_file.flush()  # 确保写入到文件
            count += 1
            print(f"Python: wrote 'test1' {count} times")
        except IOError:
            # 如果无法获取文件锁，就等一会再试
            time.sleep(1)
        finally:
            # 解锁文件
            fcntl.flock(lock_file, fcntl.LOCK_UN)
    # 等待一下，给另一个程序一些时间来获取锁
    time.sleep(1)

