"""
一个简单的 MicroPython 双核示例
"""


import _thread
import time
from machine import Pin
# 定义将在 Core 1 上运行的任务
def task_on_core1():
    led = Pin(25, Pin.OUT)
    while True:
        led.toggle()
        time.sleep(1)  # 快速闪烁

# 在 Core 0 上运行的主程序
def main():
    # 启动新线程，任务将在 Core 1 上执行
    _thread.start_new_thread(task_on_core1, ())

    # Core 0 继续执行其他任务
    counter = 0
    while True:
        print(f"Core 0 counting: {counter}")
        counter += 1
        time.sleep(1)  # 慢速计数

if __name__ == "__main__":
    main()