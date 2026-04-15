import usb_data
import time
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.preprocessing.sequence import pad_sequences # type: ignore

from Serial_Read import motion_names

import threading as th

# motion_names = ['RightAngle', 'SharpAngle', 'Lightning', 'Triangle', 
#                 'Letter_h', 'letter_R', 'letter_W', 'letter_phi', 
#                 'Circle', 'UpAndDown', 'Horn', 'Wave', 'NoMotion']


def load_norm_params():
    """加载训练时保存的归一化参数"""
    norm_params = np.load('norm_params.npy', allow_pickle=True).item()
    mean = norm_params['mean']  # shape: (6,)
    std = norm_params['std']    # shape: (6,)
    return mean, std

def normalize_data(data, mean, std):
    """归一化数据
    data: shape (150, 6) 的原始数据
    """
    return (data - mean) / std

model = load_model('model.h5')

is_OK = False

def main():
    # 1. 初始化预测器
    global is_OK
    print("Start")

    mean,std = load_norm_params()

    mpu_data = []

    # is_OK = False

    while True:
        mpu_data.append(usb_data.get_mpu6050_data())
        if len(mpu_data) == 150:
            break
    
        
    while True:
        if is_OK:
            time.sleep(1)
            for _ in range(150):
                mpu_data.append(usb_data.get_mpu6050_data())
                mpu_data.pop(0)
            test_data = np.array(mpu_data)
            is_OK = False
        else:
            for _ in range(50):
                mpu_data.append(usb_data.get_mpu6050_data())
                mpu_data.pop(0)
                # time.sleep(0.0005)
            test_data = np.array(mpu_data)

        test_data_normalized = normalize_data(test_data, mean, std)
        result = np.expand_dims(test_data_normalized, axis=0)
        temp_data = result.astype(np.float32)

        th.Thread(target=dwa_model,args=(temp_data,)).start()

def dwa_model(temp_data):
    global is_OK
    output = model.predict(temp_data)
    # # 解析结果

    predictions = output[0]  # 形状 (13,)
    predicted_index = np.argmax(predictions)
    confidence = predictions[predicted_index]
    predicted_class = motion_names[predicted_index]

    if confidence > 0.9:
        if predicted_class != "DWA_None":
            is_OK = True
            print(f"predicted_class: {predicted_class} confidence: {confidence}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print("\n Ctrl + C")