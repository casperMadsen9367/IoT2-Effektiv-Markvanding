import time
import serial
import sqlite3
import sys
import datetime

conn = sqlite3.connect('database.db')
curs = conn.cursor()
curs.execute('''CREATE TABLE IF NOT EXISTS data
            (timestamp TEXT, value REAL)''')
conn.commit()
conn.close()

def add_data(value):
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    curs.execute("INSERT INTO data values(?, ?)", (current_time, value))
    conn.commit()
    conn.close()

ser = serial.Serial("/dev/serial0", 115200, timeout=1)
ser.flush()

print("hej")

while True:
    if ser.in_waiting > 0:
        print("hej1")
        line = ser.readline().decode('latin-1').rstrip()
        print("Received from ESP32:", line)
        try:
            value = float(line)
            add_data(value)
        except ValueError:
            print("Received invalid data from ESP32:", line)
            continue

