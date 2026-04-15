# 手势魔杖

此项目基于 

> https://github.com/lyg09270/CyberryPotter_ElectromagicWand_Basic_Project

在此感谢此项目的开源作者

> https://pico.nxez.com/getting-started/

树莓派rp2040 pico中文官网



## 项目硬件基础

- 树莓派rp2040 pico w
- esp8266 wifi芯片

    注意！此项目的树莓派rp2040 pico w 的wifi芯片是基于esp8266的wifi芯片，比树莓派官方指定的要便宜很多。这个芯片是什么不影响接下来的数据采集与训练。

- mpu6050
- 连接线4根

    一共 35+18+5=58

## 项目软件基础

- 基于python3.9
- 任意文本编辑器
- windows | linux

    此项目不会使用GPU训练，不需要很好的电脑。此项目就是基于E5 2690 V3训练的

## 项目结构介绍
- rp2-pico-20230321-unstable-v1.19.1.uf2

    这是 `树莓派rp2040 pico w` 的python固件

- rp2040_python

    这是有关于 `树莓派rp2040 pico w` python 接口示例以及采集数据的代码

- CNNTrainRaw.py

    这是训练代码

- Serial_Read.py

    这是通过串口采集数据的代码

- text_file_mode.py

    这是用本地数据做测试的代码

- TextMode.py

    这是串口数据实时推理的代码

- usb_data.py

    这是读取串口数据的代码

## 说明

此项目的主要目的在于入门CNN，希望通过这个项目了解CNN原理及其实现细节。当然会继续优化此项目。

2026/4/15