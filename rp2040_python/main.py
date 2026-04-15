"""
这是获取mpu6050的数据并且将其发送到串口的入口代码
将他上传到树莓派上他会在通电时自动运行main.py的脚本
"""

# from esp_8266_wifi import ESP8266_依托于wifi的TCP服务器
from mpu_6050 import MPU6050


mpu = MPU6050(scl_pin=5, sda_pin=4) # 请与实际的接线想匹配
mpu.calibrate()

while True:
    print(mpu.get_temp_data().get_csv())

# server = ESP8266_依托于wifi的TCP服务器(1000)


# ESP8266_依托于wifi的TCP服务器.TASK = {
#     "GET-MPU6050DATA" : lambda: mpu.get_temp_data().get_csv().encode('ascii')
# }

# while True:
#     data = server.TCP_init("DwA","7723nb7723nb")
    
#     if data is False:
#         print("正在重启 TCP 服务器")
