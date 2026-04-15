"""
这是esp 8266的服务器代码示例
"""

import utime
from machine import UART



class ESP8266_依托于wifi的TCP服务器:
    # 串口映射到GP0和GP1端口上，在使用该端口和
    # WIFI模块通讯时，不要使用GP0和GP1端口
    ESO_UART = UART(0, 9600)  # 串口0,波特率为115200
    
    TASK:dict = {}
    
    def __init__(self,timeout:int = 2000):
        self.timeout = timeout
    
    def esp_sendCMD(self, command,ack:str = "OK") -> bool:
        self.ESO_UART.write(command + '\r\n')
        start_wait = utime.ticks_ms()
        print(f'esp_sendCMD {command}')
        
        while (utime.ticks_ms() - start_wait) < self.timeout * 10:
            response = self.ESO_UART.read()
            if response:
                data = response.decode()
                print(f'esp_sendCMD {command} 消息回应 : >{data.rstrip()}<')
                if data.find(ack) >= 0:
                    return True
        print(f'esp_sendCMD {command} 超时')
        return False
    
    def esp_getData(self):
        # esp_getData0,CONNECT
        
        # esp_getData
        # +IPD,0,14:Hello ESP8266!
        # esp_getData0,CLOSED
        data = self.ESO_UART.read()
        if data:
            response = data.decode()
            print(f'esp_getData{response}')
            if response.find("WIFI GOT IP") >= 0:
                return -1,"restart"
            if response.find("+IPD") >= 0:
                
                # 找到关键位置
                n1 = response.find('+IPD,')
                n2 = response.find(',', n1 + 5)      # 第一个逗号后的逗号
                n3 = response.find(':', n2)          # 冒号位置
                
                # 提取各部分
                conn_id = int(response[n1 + 5:n2])   # 连接ID
                actual_data = response[n3 + 1:]      # 实际数据
                print(f'conn_id {conn_id} actual_data {actual_data}')
                return conn_id, actual_data
        return None, None
    
    def esp_sendData(self,ID,data:str|None):
        print(f'esp_sendData {ID} - >{data}<')
        if data is None:
            self.esp_sendCMD(f'AT+CIPSEND={ID},5')
            self.ESO_UART.write('hello')
            return
        if(data in ESP8266_依托于wifi的TCP服务器.TASK):
            req_data = ESP8266_依托于wifi的TCP服务器.TASK[data]()
            self.esp_sendCMD(f'AT+CIPSEND={ID},{len(req_data)}')
            self.ESO_UART.write(req_data)
            return
        print(ESP8266_依托于wifi的TCP服务器.TASK)
        self.esp_sendCMD(f'AT+CIPSEND={ID},3')
        self.ESO_UART.write('404')
    
    
    def _tcp_init_commed(self,wifi_name:str,password:str,port:str='7723'):
        self.esp_sendCMD("+++",ack='ERROR')
        self.esp_sendCMD("AT")
        self.esp_sendCMD('AT+CWMODE=3')
        
        while True:
            if self.esp_sendCMD(f'AT+CWJAP="{wifi_name}","{password}"',ack='WIFI GOT IP'):
                print('网络连接成功! 开启TCP服务器')
                break
        utime.sleep(2)
        self.esp_sendCMD("AT+CIPMUX=1")
        
        while True:
            if self.esp_sendCMD(f'AT+CIPSERVER=1,{port}',ack='OK'):
                print('TCP服务器开启成功!')
                break
        utime.sleep(1)
        
        self.esp_sendCMD("AT+CIFSR")
    
    def TCP_init(self,wifi_name:str,password:str,port:str='7723',) -> bool:
        self._tcp_init_commed(wifi_name,password,port)
        while True:
            try:
                ID, reponse = self.esp_getData()
                if ID != None:
                   if ID != -1:
                       self.esp_sendData(ID,reponse)
                   else:
                       return False
                
            except Exception as e:
                print(f'Error: {e}')
                return False

class ESP8266_热点TCP服务器:
    
    ESO_UART = UART(0, 115200)  # 串口0,波特率为115200
    
    def __init__(self,wifi_name:str,password:str,port:str='7723',timeout:int=2000):
        self.wifi_name = wifi_name
        self.password = password
        self.port = port
        self.timeout = timeout
    
    
    def send_CMD(self,command:str,ack:str):
        self.ESO_UART.write(command + '\r\n')
        start_wait = utime.ticks_ms()
        print(f'esp_sendCMD {command}')
        
        while (utime.ticks_ms() - start_wait) < self.timeout * 10:
            response = self.ESO_UART.read()
            if response:
                data = response.decode()
                print(f'esp_sendCMD {command} 消息回应 : >{data.rstrip()}<')
                if data.find(ack) >= 0:
                    return True
        print(f'esp_sendCMD {command} 超时')
        return False
    
    def TCP_init(self):
        pass

class ESP8266_连接热点直传数据:
    ESO_UART = UART(0, 115200)
    TASK:dict = {}
    
    def __init__(self,timeout:int) -> None:
        self.timeout = timeout

    def esp_sendCMD(self, command,ack:str = "OK") -> bool:
        self.ESO_UART.write(command + '\r\n')
        start_wait = utime.ticks_ms()
        print(f'esp_sendCMD {command}')
        
        while (utime.ticks_ms() - start_wait) < self.timeout * 10:
            response = self.ESO_UART.read()
            if response:
                data = response.decode()
                print(f'esp_sendCMD {command} 消息回应 : >{data.rstrip()}<')
                if data.find(ack) >= 0:
                    return True
        print(f'esp_sendCMD {command} 超时')
        return False
    
    def esp_getData(self):
        # esp_getData0,CONNECT
        
        # esp_getData
        # +IPD,0,14:Hello ESP8266!
        # esp_getData0,CLOSED
        data = self.ESO_UART.read()
        if data:
            response = data.decode()
            print(f'esp_getData{response}')
            if response.find("WIFI GOT IP") >= 0:
                return -1,"restart"
            if response.find("+IPD") >= 0:
                
                # 找到关键位置
                n1 = response.find('+IPD,')
                n2 = response.find(',', n1 + 5)      # 第一个逗号后的逗号
                n3 = response.find(':', n2)          # 冒号位置
                
                # 提取各部分
                conn_id = int(response[n1 + 5:n2])   # 连接ID
                actual_data = response[n3 + 1:]      # 实际数据
                print(f'conn_id {conn_id} actual_data {actual_data}')
                return conn_id, actual_data
        return None, None
    
    def esp_sendData(self,ID,data:str|None):
        print(f'esp_sendData {ID} - >{data}<')
        if(data in ESP8266_连接热点直传数据.TASK):
            while True:
                req_data = ESP8266_连接热点直传数据.TASK[data]()
                self.esp_sendCMD(f'AT+CIPSEND={ID},{len(req_data)}','OK')
                self.ESO_UART.write(req_data)
        print(ESP8266_连接热点直传数据.TASK)
        self.esp_sendCMD(f'AT+CIPSEND={ID},3')
        self.ESO_UART.write('404')
    
    
    def _tcp_init_commed(self,wifi_name:str,password:str,port:str='7723'):
        self.esp_sendCMD("+++",ack='ERROR')
        self.esp_sendCMD("AT")
        self.esp_sendCMD('AT+CWMODE=3')
        
        while True:
            if self.esp_sendCMD(f'AT+CWJAP_CUR="{wifi_name}","{password}"',ack='WIFI GOT IP'):
                print('网络连接成功! 开启TCP服务器')
                break
        utime.sleep(2)
        self.esp_sendCMD("AT+CIPMUX=1")
        
        while True:
            if self.esp_sendCMD(f'AT+CIPSERVER=1,{port}',ack='OK'):
                print('TCP服务器开启成功!')
                break
        utime.sleep(1)
        
        self.esp_sendCMD("AT+CIFSR")
    
    def TCP_init(self,wifi_name:str,password:str,port:str='7723',) -> bool:
        self._tcp_init_commed(wifi_name,password,port)
        while True:
            try:
                ID, reponse = self.esp_getData()
                if ID != None:
                   if ID != -1:
                       self.esp_sendData(ID,reponse)
                   else:
                       return False
                
            except Exception as e:
                print(f'Error: {e}')
                return False
