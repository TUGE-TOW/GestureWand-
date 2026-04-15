"""
MPU-6050 六轴传感器读取脚本 for Raspberry Pi Pico (RP2040)
接线：VCC->3V3, GND->GND, SCL->GP5, SDA->GP4, AD0->GND(可选)
"""

import math
import time

from machine import I2C, Pin


class MPU6050_temp_data:
    def __init__(
        self,
        accel_g: list[float],
        temp_c: float,
        gyro_dps: list[float],
        pitch: float,
        roll: float,
    ):
        self.accel_g = accel_g
        self.temp_c = temp_c
        self.gyro_dps = gyro_dps
        self.pitch = pitch
        self.roll = roll

    def __str__(self):
        return f"accel_g: {self.accel_g}, temp_c: {self.temp_c}, gyro_dps: {self.gyro_dps}, pitch: {self.pitch}, roll: {self.roll}"

    def __repr__(self):
        return f"MPU6050_temp_data(accel_g={self.accel_g}, temp_c={self.temp_c}, gyro_dps={self.gyro_dps}, pitch={self.pitch}, roll={self.roll})"

    def get_csv(self) -> str:
        return f"{self.accel_g[0]},{self.accel_g[1]},{self.accel_g[2]},{self.gyro_dps[0]},{self.gyro_dps[1]},{self.gyro_dps[2]},{self.pitch},{self.roll}"
    
    def get_no_temp_dict(self) -> dict:
        return {
            "accel_g": self.accel_g,
            "gyro_dps": self.gyro_dps,
            "pitch": self.pitch,
            "roll": self.roll,
        }
    
    def get_temp_c(self) -> float:
        return self.temp_c

class MPU6050:
    # MPU6050 寄存器地址
    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H = 0x43
    TEMP_OUT_H = 0x41

    def __init__(
        self,
        scl_pin: int,
        sda_pin: int,
        address: int = 0x68,
        i2c_id=0,
    ):
        self.i2c = I2C(i2c_id, scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.addr = address

        self.i2c.scan()

        print(f"找到MPU6050，地址: 0x{self.addr:02x}")

        self.i2c.writeto_mem(self.addr, self.PWR_MGMT_1, b"\x00")
        time.sleep(0.1)
        self.i2c.writeto_mem(self.addr, 0x1C, b"\x00")
        self.i2c.writeto_mem(self.addr, 0x1B, b"\x00")

        self.accel_offset = [0, 0, 0]
        self.gyro_offset = [0, 0, 0]
        self.temp_offset = 0

        print("MPU6050初始化完成")

    def _read_word(self, reg_addr):
        """读取16位有符号数据"""
        data = self.i2c.readfrom_mem(self.addr, reg_addr, 2)
        value = (data[0] << 8) | data[1]
        return value if value < 32768 else value - 65536

    def _read_words(self, reg_addr, count):
        """连续读取多个16位数据"""
        data = self.i2c.readfrom_mem(self.addr, reg_addr, count * 2)
        values = []
        for i in range(0, len(data), 2):
            val = (data[i] << 8) | data[i + 1]
            if val >= 32768:
                val -= 65536
            values.append(val)
        return values

    def get_raw_data(self):
        """一次性读取所有原始数据（高效）"""
        # 从0x3B开始连续读取14字节：6字节加速度 + 2字节温度 + 6字节陀螺仪
        data = self.i2c.readfrom_mem(self.addr, self.ACCEL_XOUT_H, 14)

        # 解析加速度 (原始值)
        accel_x = (data[0] << 8) | data[1]
        accel_y = (data[2] << 8) | data[3]
        accel_z = (data[4] << 8) | data[5]
        if accel_x >= 32768:
            accel_x -= 65536
        if accel_y >= 32768:
            accel_y -= 65536
        if accel_z >= 32768:
            accel_z -= 65536

        # 解析温度
        temp = (data[6] << 8) | data[7]
        if temp >= 32768:
            temp -= 65536

        # 解析陀螺仪
        gyro_x = (data[8] << 8) | data[9]
        gyro_y = (data[10] << 8) | data[11]
        gyro_z = (data[12] << 8) | data[13]
        if gyro_x >= 32768:
            gyro_x -= 65536
        if gyro_y >= 32768:
            gyro_y -= 65536
        if gyro_z >= 32768:
            gyro_z -= 65536

        return [accel_x, accel_y, accel_z], temp, [gyro_x, gyro_y, gyro_z]

    def get_calibrated_data(self):
        """获取校准后的物理量数据"""
        accel_raw, temp_raw, gyro_raw = self.get_raw_data()

        # 转换为物理量 (根据当前量程设置)
        # 加速度: ±2g = 16384 LSB/g
        accel_g = [
            a / 16384.0 - offset for a, offset in zip(accel_raw, self.accel_offset)
        ]

        # 温度: 公式来自数据手册
        temperature = temp_raw / 340.0 + 36.53 - self.temp_offset

        # 陀螺仪: ±250°/s = 131 LSB/°/s
        gyro_dps = [g / 131.0 - offset for g, offset in zip(gyro_raw, self.gyro_offset)]

        return accel_g, temperature, gyro_dps

    def calibrate(self, samples=500):
        """自动校准传感器（保持传感器水平静止）"""
        print(f"开始校准，采集 {samples} 个样本...")

        accel_sum = [0, 0, 0]
        gyro_sum = [0, 0, 0]
        temp_sum = 0

        for i in range(samples):
            accel_raw, temp_raw, gyro_raw = self.get_raw_data()

            for j in range(3):
                accel_sum[j] += accel_raw[j]
                gyro_sum[j] += gyro_raw[j]
            temp_sum += temp_raw

            if i % 50 == 0:
                print(f"  进度: {i}/{samples}")
            time.sleep(0.01)

        # 计算平均值和偏移量
        # 期望：静止时加速度Z轴=1g，X,Y轴=0；陀螺仪各轴=0
        self.accel_offset = [
            accel_sum[0] / samples / 16384.0,  # X轴偏移
            accel_sum[1] / samples / 16384.0,  # Y轴偏移
            accel_sum[2] / samples / 16384.0 - 1.0,  # Z轴偏移（减去1g重力）
        ]

        self.gyro_offset = [g / samples / 131.0 for g in gyro_sum]
        self.temp_offset = (temp_sum / samples) / 340.0

        print("校准完成!")
        print(
            f"  加速度偏移: X={self.accel_offset[0]:.4f}g, Y={self.accel_offset[1]:.4f}g, Z={self.accel_offset[2]:.4f}g"
        )
        print(
            f"  陀螺仪偏移: X={self.gyro_offset[0]:.2f}°/s, Y={self.gyro_offset[1]:.2f}°/s, Z={self.gyro_offset[2]:.2f}°/s"
        )

    def get_pitch_roll(self, accel_g):
        """从加速度计算俯仰和横滚角（简化）"""
        ax, ay, az = accel_g

        # 计算俯仰角 (绕X轴旋转)
        pitch = math.atan2(ay, math.sqrt(ax**2 + az**2)) * 180 / math.pi

        # 计算横滚角 (绕Y轴旋转)
        roll = math.atan2(-ax, math.sqrt(ay**2 + az**2)) * 180 / math.pi

        return pitch, roll

    def get_temp_data(self) -> MPU6050_temp_data:
        accel_g, temp_c, gyro_dps = self.get_calibrated_data()
        pitch, roll = self.get_pitch_roll(accel_g)

        return MPU6050_temp_data(accel_g, temp_c, gyro_dps, pitch, roll)


if __name__ == "__main__":
    import time

    mpu = MPU6050(scl_pin=13, sda_pin=12)
    print("请校准传感器,两秒后开始显示传感器信息")
    time.sleep(2)
    mpu.calibrate()

    while True:
        data = mpu.get_temp_data()
        print(data)
        print(f"温度 {data.temp_c}")
        time.sleep(2)
