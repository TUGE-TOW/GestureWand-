import usb_data
import time

SAVE_PATH = "CS_DATA"
TASK_NAME = "DWA_▽"

ONE_TASK_CONNECT = 150
TASK_CONNECT = 1000

motion_names = ['DWA_None', 'DWA_Circle','DWA_RL','DWA_W','DWA_▽']

def main():
    for i in range(TASK_CONNECT):
        print(f" {i} >>>",end=" ")
        print()
        # input()
        with open(f"{SAVE_PATH}/{TASK_NAME}_{i}.txt","w") as file:
            for _ in range(ONE_TASK_CONNECT):
                time.sleep(0.01)
                file.write(" ".join(usb_data.get_mpu6050_data_str()).rstrip() + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print("\n Ctrl + C")

