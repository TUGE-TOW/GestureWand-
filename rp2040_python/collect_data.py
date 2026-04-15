"""
这是尝试使用无线采集mpu6050数据的客户端代码
由于采集的频率较低和不稳定,被弃用了.
"""


import socket

# from pathlib import Path as path

def connect_rp2040(ip, port,sample_size:int=10):
    try:
        # 创建TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        # 连接服务器
        print(f"尝试连接 {ip}:{port}...")
        sock.connect((ip, port))
        print("✓ 连接成功!")
        
        input("按回车键继续...")
        
        for i in range(sample_size):
            sock.send("GET-MPU6050DATA".encode())
            response = sock.recv(1024)
            print(response)
        
        sock.close()
        
    except Exception as e:
        print(f"✗ 连接错误: {e}")

# test_tcp_server("192.168.127.53", 7723)

if __name__ == "__main__":
    connect_rp2040("192.168.176.53", 7723,20)