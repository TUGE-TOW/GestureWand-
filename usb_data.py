import serial


ser = serial.Serial("/COM3", 115200) # 请根据实际情况更改



def get_mpu6050_data() -> list[float]:
    while True:
        try:
            usb_text = ser.readline().decode()
        except Exception as e:
            print(e)
            continue
        data = usb_text.split(" ")
        if len(data) == 6:
            return  [float(i) for i in data]


def get_mpu6050_data_str() -> str:
    while True:
        try:
            usb_text = ser.readline().decode()
        except Exception as e:
            print(e)
            continue
        data = usb_text.split(" ")
        if len(data) == 6:
            return  data

def main():
    if ser.isOpen() is False:
       print("打开串口失败。")
       return

    while True:
        print(get_mpu6050_data())

if __name__ == "__main__":
    main()
    # print(serial.Serial())

