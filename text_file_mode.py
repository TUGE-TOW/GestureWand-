import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.preprocessing.sequence import pad_sequences # type: ignore
import os
import re
from Serial_Read import motion_names

# motion_names = ['RightAngle', 'SharpAngle', 'Lightning', 'Triangle', 
                # 'Letter_h', 'letter_R', 'letter_W', 'letter_phi', 
                # 'Circle', 'UpAndDown', 'Horn', 'Wave', 'NoMotion']

DEF_SAVE_TO_PATH = './CS_DATA/'
DEF_MODEL_NAME = 'model.h5'
DEF_MODEL_H_NAME = 'weights.h'
DEF_FILE_MAX = 300
#DEF_N_ROWS = 60
DEF_N_ROWS = 150
DEF_USE_COLS = (0,1,2,3,4,5)

# 文件格式
DEF_FILE_FORMAT = '.txt'
# 文件名分隔符
DEF_FILE_NAME_SEPERATOR = '_'
motion_to_label = {name: idx for idx, name in enumerate(motion_names)}


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


# 加载数据集
def load_dataset(root_dir, max_rows=None):
    file_list = []
    labels = []
    for filename in os.listdir(root_dir):
        if filename.endswith(DEF_FILE_FORMAT):
            match = re.match(rf'^([\w]+)_([\d]+){DEF_FILE_FORMAT}$', filename)
            if match:
                motion_name = match.group(1)
                number_str = match.group(2)
                number = int(number_str)
                if 0 <= number <= DEF_FILE_MAX:
                    if motion_name in motion_to_label:
                        file_path = os.path.join(root_dir, filename)
                        # 使用max_rows参数限制读取的行数
                        data = np.loadtxt(file_path, delimiter=' ', usecols=DEF_USE_COLS, max_rows=max_rows)
                        file_list.append(data)
                        labels.append(motion_to_label[motion_name])
                    else:
                        print(f"Motion name not recognized: {filename}")
                else:
                    print(f"Number out of range: {filename}")
            else:
                print(f"Invalid file name format: {filename}")
    return file_list, labels


def main():
    # 1. 初始化预测器
    model = load_model('model.h5')
    print("Start")
    
    mean,std = load_norm_params()

    file_list, labels = load_dataset(DEF_SAVE_TO_PATH, max_rows=DEF_N_ROWS)

    TP = 0
    FP = 0

    for i in range(1,len(labels) - 1,2):
        mpu_data = file_list[i]

        test_data = np.array(mpu_data)

        test_data_normalized = normalize_data(test_data, mean, std)
        result = np.expand_dims(test_data_normalized, axis=0)
        temp_data = result.astype(np.float32)


        output = model.predict(temp_data)
        # # 解析结果

        predictions = output[0]  # 形状 (13,)
        predicted_index = np.argmax(predictions)
        confidence = predictions[predicted_index]
        predicted_class = motion_names[predicted_index]

        print(motion_names[labels[i]].center(50,'-'))

        if confidence > 0.8 and motion_names[labels[i]] == predicted_class:
            TP += 1
            print(f"predicted_class: {predicted_class}")
        else:
            FP += 1
            print("没有识别出来")
        print('end'.center(50,'-'))
        # print(f"predictions: {predictions} predicted_index: {predicted_index} confidence: {confidence} predicted_class: {predicted_class}")
        # # 5. 显示所有类别概率
        # print("\n=== 所有类别概率 ===")
        # for i, name in enumerate(motion_names):
        #     if probs[i] > 0.01:
        #         print(f"{name}: {probs[i]:.4f}")


    print(f"TP: {TP} FP: {FP} TP/FP: {TP/(FP + TP)}")
if __name__ == "__main__":
    main()
    # file_list, labels = load_dataset(DEF_SAVE_TO_PATH, max_rows=DEF_N_ROWS)

    # print(file_list[len(labels) - 1])
    # print(labels)

