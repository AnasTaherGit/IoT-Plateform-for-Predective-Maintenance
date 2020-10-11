import machine
import time
from math import log
import umqtt.robust as mqtt
import ubinascii
import utime
import math


N = const(2000)
n = 0
wait_time = const(10000)
Start_State = False
Topic_pub = b"System/Vibration"
Topic_pub_2 = b"System/Start"
Topic_sub_0 = b"System/esp_configuration"
Topic_sub_1 = b"System/esp_configuration/frequence"
Topic_sub_2 = b"System/esp_configuration/BrokerAdress"
freq = 1000
ID = ubinascii.hexlify(machine.unique_id())
Broker = "192.168.0.106"
# Configuring the system
DataBuffer = bytearray(N*8)

i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=300000)
led = machine.Pin(2, machine.Pin.OUT)
MPU_ADRESS = 104
ACCEL_REG = 0x3B
PWR_MGMT_1_REG = 0x6B
DATA = bytearray(6)
ax, ay, az, t = 0.0, 0.0, 0.0, 0
i2c.writeto_mem(MPU_ADRESS, PWR_MGMT_1_REG, b'\x00')


def timeit(f, *args, **kwargs):
    def foo(*args, **kwargs):
        t = utime.ticks_us()
        result = f(*args, **kwargs)
        delta = utime.ticks_diff(utime.ticks_us(), t)
        print("Execution time : {:6.3f}ms".format(delta / 1000))
        return result
    return foo


def Configuration_Handler(Topic, msg):
    global freq, Broker, Start_State
    if Topic == Topic_sub_0:
        Start_State = True
        print("Start Opération")
    elif Topic == Topic_sub_1:
        freq = int(msg)
        print(freq)
    elif Topic == Topic_sub_2:
        Broker = msg.decode('utf-8')
        print(Broker)


def GetDatafromBuffer(i, Origin):
    global DataBuffer
    t = utime.ticks_diff(utime.ticks_ms(), Origin)
    DataBuffer[i] = DATA[0]      # ACCEL_X_H
    DataBuffer[i+1] = DATA[1]    # ACCEL_X_L
    DataBuffer[i+2] = DATA[2]    # ACCEL_Y_H
    DataBuffer[i+3] = DATA[3]    # ACCEL_Y_L
    DataBuffer[i+4] = DATA[4]    # ACCEL_Z_H
    DataBuffer[i+5] = DATA[5]    # ACCEL_Z_L
    DataBuffer[i+6] = (t & 0xFF00)//0x100
    DataBuffer[i+7] = t & 0x00FF


def dataConvert(n):
    if (n >= math.pow(2, 15)):
        n = n-math.pow(2, 16)
    n = n/16384
    return n


def JSONformat(data):
    s = '{"accelerometer_x":' + '{}'.format(dataConvert(data[0] << 8 | data[1])) + ',"accelerometer_y":' + '{}'.format(
        dataConvert(data[2] << 8 | data[3])) + ',"accelerometer_z":' + '{}'.format(dataConvert(data[4] << 8 | data[5])) + ',"localEpoch":' + '{}'.format(data[6] << 8 | data[7]) + "}"
    return s


def Publish(client):
    global Start_State
    temp = bytearray(8)
    for i in range(0, N*8, 8):
        for j in range(8):
            temp[j] = DataBuffer[i+j]
        client.publish(Topic_pub, JSONformat(temp))
    Start_State = False


def main():
    client = mqtt.MQTTClient(ID, Broker, port=1883)
    client.set_callback(Configuration_Handler)
    print("CallBack function set")
    client.connect()
    print("Connected")
    client.subscribe(Topic_sub_1)
    client.subscribe(Topic_sub_2)
    client.subscribe(Topic_sub_0)
    while 1:
        client.check_msg()
        utime.sleep_ms(10)
        if Start_State:
            print("Begin Collection")
            Origin = utime.ticks_ms()
            for i in range(0, N*8, 8):
                i2c.readfrom_mem_into(MPU_ADRESS, ACCEL_REG, DATA)
                GetDatafromBuffer(i, Origin)
            try:
                client.publish(Topic_pub_2, "START")
                utime.sleep_ms(20)
                Publish(client)
            except OSError as E:
                print("Error", E)
                i2c.writeto_mem(MPU_ADRESS, PWR_MGMT_1_REG, b'\x00')
                client.reconnect()
        utime.sleep_ms(wait_time)


if __name__ == '__main__':
    main()
