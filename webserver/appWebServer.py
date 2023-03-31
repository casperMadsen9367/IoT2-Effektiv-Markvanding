from flask import Flask, render_template
import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import sqlite3
import time
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from threading import Thread
import serial
import sys
import RPi.GPIO as GPIO

app = Flask(__name__)

GPIO.setwarnings(False)

red_pin = 2
green_pin = 4
yellow_pin = 3
GPIO.setmode(GPIO.BCM)
GPIO.setup(red_pin, GPIO.OUT)
GPIO.setup(green_pin, GPIO.OUT)
GPIO.setup(yellow_pin, GPIO.OUT)

ser = serial.Serial("/dev/serial0", 115200, timeout=1)
ser.flush()

def add_data(value):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    c.execute("INSERT INTO data values(?, ?)", (current_time, value))
    conn.commit()
    conn.close()

def get_data():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM data")
    data = c.fetchall()
    conn.close()
    return data

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/omos')
def omos():
    return render_template('omos.html')

@app.route('/dataside')
def dataside():
    data = get_data()
    x = [datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f') for row in data]
    y = [row[1] for row in data]
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
    fig.add_trace(go.Scatter(x=x, y=y, name='Random Data'))
    fig.update_layout(title='Jordfugtighedsgraf', xaxis_title='Tid', yaxis_title='Fugtighed i procent')
    plot = fig.to_html(full_html=False)
    return render_template('dataside.html', plot=plot)

def update_plot():
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('latin-1').rstrip()
            print("Received from ESP32:", line)
            time.sleep(5)
            try:
                value1 = float(line)
                add_data(value1)
                if value1 > 45:
                    GPIO.output(red_pin, GPIO.LOW)
                    GPIO.output(green_pin, GPIO.LOW)
                    GPIO.output(yellow_pin, GPIO.HIGH)
                elif 35 <= value1 <= 45:
                    GPIO.output(red_pin, GPIO.LOW)
                    GPIO.output(green_pin, GPIO.HIGH)
                    GPIO.output(yellow_pin, GPIO.LOW)
                else:
                    GPIO.output(red_pin, GPIO.HIGH)
                    GPIO.output(green_pin, GPIO.LOW)
                    GPIO.output(yellow_pin, GPIO.LOW)
            except ValueError:
                print("Received invalid data from ESP32:", line)
                continue

if __name__ == '__main__':
    import os
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute('''CREATE TABLE IF NOT EXISTS data
                (timestamp TEXT, value REAL)''')
    conn.commit()
    conn.close()
    Thread(target=update_plot).start()
    app.run(host="0.0.0.0", port= 5056, debug=True)

