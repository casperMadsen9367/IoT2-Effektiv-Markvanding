import machine
import time
import ujson
from time import sleep
from machine import Pin, I2C

uart = machine.UART(2, baudrate=115200, tx=17, rx=16)
sensor_pin = 34

MCP3021_I2C_ADDRESS = 0x49
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000)

def read_mcp3021():
    i2c.writeto(MCP3021_I2C_ADDRESS, b'')
    data = i2c.readfrom(MCP3021_I2C_ADDRESS, 2)
    value = ((data[0] & 0x03) << 8) | data[1]

    moisture = round((value * 100) / 1024, 1)

    return moisture

while True:
    sensor_data = read_mcp3021()
    json_data = str(sensor_data)
    uart.write(json_data.encode('latin-1') + b'\n')
    print(sensor_data)
    time.sleep(5)

