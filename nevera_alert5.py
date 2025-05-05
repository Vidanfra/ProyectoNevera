# This script monitors the power supply to a refrigerator using a Raspberry Pi and a BME280 sensor.
# It sends email alerts when the power is cut off and when it is restored. 
# The script also serves a web page displaying the current temperature, humidity, and pressure readings.
# The script uses Flask for the web server and RPi.GPIO for GPIO pin control.
# Script created by Vicente Danvila Fraile, 16-12-2024

# Create the project directory
# mkdir -p ~/ProyectoNevera
# cd ~/ProyectoNevera

# Create the virtual environment
# python3 -m venv ProyectoNevera

# Activate the virtual environment
# source ProyectoNevera/bin/activate

# Upgrade pip (optional but recommended)
# pip install --upgrade pip

# Install required Python packages
# pip install adafruit-circuitpython-bme280 flask

# To copy the script to the Raspberry Pi:
# scp C:\Users\vicente.danvila\Desktop\PROJECTS\ProyectoNevera\nevera_alert5.py pi@10.144.169.135:ProyectoNevera/

import threading
from flask import Flask, jsonify, render_template_string
import RPi.GPIO as GPIO
import smtplib
from email.message import EmailMessage
import time
import board  # Don't use "pip install board", it's a different libraty from adafruit-blinka
from adafruit_bme280 import basic as adafruit_bme280  # pip install adafruit-circuitpython-bme280 (venv)
import csv
import os
import mpld3  # pip install mpld3
import matplotlib.pyplot as plt  # pip install matplotlib
import numpy as np

# Configurable variables
POLLING_INTERVAL = 1  # Time to sleep in seconds between checks
SEA_LEVEL_PRESSURE = 1016  # Pressure at sea level (Valencia, 16-12-2024)
POWER_PIN = 26  # GPIO pin used for power input monitoring
EMAIL_RECIPIENTS = ["vicentedf88@gmail.com"]  # Add more recipients if needed

# Email credentials (hardcoded for now)
EMAIL_USER = "vicentedanvilaf@gmail.com"
EMAIL_PASSWORD = "ubjwhhbazadlmrii"  # Replace this with your application password of your Google account

# CSV file path
DATA_FILE_PATH = 'data/data_log.csv'

# Flask setup
app = Flask(__name__)
server_data = {
    "temperature": None,
    "humidity": None,
    "pressure": None,
    "timestamp": None,
    "power_supply": "OFF"
}

# Flask route for the web page
@app.route('/')  # <- THIS LINE FIXES YOUR 404 ERROR
def index():
    # Return rendered template with embedded graph and current values
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Monitorización Chalet</title>
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    background-color: #f4f7fc;
                    padding: 20px;
                    color: #333;
                }
                h1 {
                    color: #4CAF50;
                    text-align: center;
                    margin-bottom: 30px;
                }
                .content {
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    max-width: 800px;
                    margin: 0 auto;
                }
                .timestamp {
                    font-size: 16px;
                    color: #777;
                }
                .plot-container {
                    margin-top: 40px;
                }
            </style>
        </head>
        <body>
            <div class="content">
                <h1>Monitorización del Chalet</h1>
                <p class="timestamp"><strong>Fecha y Hora:</strong> {{ timestamp }}</p>
                <p><strong>Suministro eléctrico:</strong> {{ power_supply }}</p>
                <p><strong>Temperatura:</strong> {{ temperature }} ºC</p>
                <p><strong>Humedad:</strong> {{ humidity }} %</p>
                <p><strong>Presión:</strong> {{ pressure }} hPa</p>
                <div class="plot-container">
                    {{ plot_html | safe }}
                </div>
            </div>
        </body>
        </html>
    ''', plot_html=plot_html(), **server_data)

def plot_html():
    if not os.path.exists(DATA_FILE_PATH):
        print("None CSV file found. No data to plot.")
        return 0

    # Read CSV data using DictReader for named access
    timestamps = []
    temperatures = []
    humidities = []
    pressures = []

    with open(DATA_FILE_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamps.append(row["timestamp"])
            temperatures.append(float(row["temperature"]))
            humidities.append(float(row["humidity"]))
            pressures.append(float(row["pressure"]))

    # Plotting with matplotlib
    fig, axs = plt.subplots(3, 1, sharex=True)
    axs[0].set_title('Temperatura (°C)')
    axs[0].plot(timestamps, temperatures, color='red')
    axs[0].set_ylabel('°C')

    axs[1].set_title('Humedad (%)')
    axs[1].plot(timestamps, humidities, color='blue')
    axs[1].set_ylabel('%')

    axs[2].set_title('Presión (hPa)')
    axs[2].plot(timestamps, pressures, color='green')
    axs[2].set_ylabel('hPa')
    axs[2].set_xlabel('Tiempo')

    plt.tight_layout()

    # Convert plot to HTML
    plot_html = mpld3.fig_to_html(fig)

    return plot_html

# Function to send an email alert
def emailAlert(subject, body, to):
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['subject'] = subject
        msg['to'] = to
        msg['from'] = EMAIL_USER

        # Connect to the SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print("Email de alerta enviado correctamente")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

# Function to send alert with BME280 data
def sendAlert(bme):
    local_time = time.localtime(time.time())
    time_string = time.strftime("%H:%M:%S, %d/%m/%Y", local_time)

    subject = "Nevera sin electricidad!"
    body = (
        f"¡El suministro eléctrico en el chalet se ha cortado a las {time_string}!\n"
        f"Las condiciones del chalet en este momento son:\n"
        f"\tTEMPERATURA: {bme.temperature:.1f} ºC\n"
        f"\tHUMEDAD: {bme.relative_humidity:.1f} %\n"
        f"\tPRESIÓN: {bme.pressure:.1f} hPa\n"
        "¡Acuda a rearmar el cuadro eléctrico antes de que la comida se pudra "
        "y se llene de gusanos otra vez!\n\n"
        "Muchas gracias. Un saludo!"
    )

    for recipient in EMAIL_RECIPIENTS:
        emailAlert(subject, body, recipient)

    print("\tEmail de alerta por el corte de suministro enviado")
    print(f"\n\tAsunto: {subject}")
    print(f"\n\tCuerpo: {body}")

# Function to send alert with BME280 data
def sendRecovery(bme):
    local_time = time.localtime(time.time())
    time_string = time.strftime("%H:%M:%S, %d/%m/%Y", local_time)

    subject = "Suministro eléctrico recuperado!"
    body = (
        f"¡Tras el corte eléctrico, el suministro eléctrico en el chalet se ha recuperado a las {time_string}!\n"
        f"Las condiciones del chalet en este momento son:\n"
        f"\tTEMPERATURA: {bme.temperature:.1f} ºC\n"
        f"\tHUMEDAD: {bme.relative_humidity:.1f} %\n"
        f"\tPRESIÓN: {bme.pressure:.1f} hPa\n"

        "Muchas gracias. Un saludo!"
    )

    for recipient in EMAIL_RECIPIENTS:
        emailAlert(subject, body, recipient)

    print("\tEmail informando de la recuperación del suministro enviado")
    print(f"\n\tAsunto: {subject}")
    print(f"\n\tCuerpo: {body}")

# Function to send alert with BME280 data
def sendInit(bme):
    local_time = time.localtime(time.time())
    time_string = time.strftime("%H:%M:%S, %d/%m/%Y", local_time)

    subject = "El sistema de monitorización se ha iniciado!"
    body = (
        f"¡El sistema de monitorización del suministro eléctrico en el chalet se ha iniciado a las {time_string}!\n"
        f"Las condiciones del chalet en este momento son:\n"
        f"\tTEMPERATURA: {bme.temperature:.1f} ºC\n"
        f"\tHUMEDAD: {bme.relative_humidity:.1f} %\n"
        f"\tPRESIÓN: {bme.pressure:.1f} hPa\n"

        "Muchas gracias. Un saludo!"
    )

    for recipient in EMAIL_RECIPIENTS:
        emailAlert(subject, body, recipient)

    print("\tEmail informando del inicio del programa de monitorización del suministro eléctrico enviado")
    print(f"\n\tAsunto: {subject}")
    print(f"\n\tCuerpo: {body}")

# Function to create and initialize the BME280 sensor
def createWeatherSensor():
    try:
        # Create sensor object, using the board's default I2C bus
        i2c = board.I2C()  # uses board.SCL and board.SDA
        bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
        bme.sea_level_pressure = SEA_LEVEL_PRESSURE
        return bme
    except Exception as e:
        print(f"Error initializing BME280 sensor: {e}")
        return None

# Function to display weather data
def showWeather(bme):
    print("\nCondiciones actuales del chalet:")
    print(f"\tTemperatura: {bme.temperature:.1f} ºC")
    print(f"\tHumedad: {bme.relative_humidity:.1f} %")
    print(f"\tPresión: {bme.pressure:.1f} hPa")

# GPIO setup validation
def validateGPIO(pin):
    state = GPIO.input(pin)
    print(f"Estado inicial del pin {pin}: {'ON' if state else 'OFF'}")

# Web Monitoring functions
def updateServerData(bme, power):
    server_data["temperature"] = f"{bme.temperature:.1f}"
    server_data["humidity"] = f"{bme.relative_humidity:.1f}"
    server_data["pressure"] = f"{bme.pressure:.1f}"
    server_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    server_data["power_supply"] = "ON" if not power else "OFF"

class Logger:
    def __init__(self):
        self.data_dict = {
            "temperature": [],
            "humidity": [],
            "pressure": [],
            "timestamp": None,
            "power_supply": "OFF"
        }
    def log_data(self, instant_data):
        self.data_dict["temperature"].append(float(instant_data["temperature"]))
        self.data_dict["humidity"].append(float(instant_data["humidity"]))
        self.data_dict["pressure"].append(float(instant_data["pressure"]))
        self.data_dict["timestamp"] = instant_data["timestamp"]
        self.data_dict["power_supply"] = instant_data["power_supply"]

    def log_csv(self):
        # Calculate the average values
        avg_data = {
            "temperature": sum(self.data_dict["temperature"]) / len(self.data_dict["temperature"]),
            "humidity": sum(self.data_dict["humidity"]) / len(self.data_dict["humidity"]),
            "pressure": sum(self.data_dict["pressure"]) / len(self.data_dict["pressure"]),
            "timestamp": self.data_dict["timestamp"],
            "power_supply": self.data_dict["power_supply"]
        }
        # Clear the data dictionary for the next logging period
        self.data_dict["temperature"].clear()
        self.data_dict["humidity"].clear()
        self.data_dict["pressure"].clear()

        # Create the directory if it doesn't exist
        os.makedirs('data', exist_ok=True)

        # Write the data to a CSV file
        write_header = not os.path.exists(DATA_FILE_PATH)

        with open(DATA_FILE_PATH, 'a', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            if write_header:
                writer.writerow(["timestamp", "temperature", "humidity", "pressure", "power_supply"])
            writer.writerow([
                avg_data["timestamp"],
                f"{avg_data['temperature']:.1f}",
                f"{avg_data['humidity']:.1f}",
                f"{avg_data['pressure']:.1f}",
                avg_data["power_supply"]
            ])


def flaskThread():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

# Main program
if __name__ == '__main__':
    print("Iniciando...")

    # Initialize GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(POWER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Initialize the BME280 sensor
    bme280 = createWeatherSensor()
    if bme280 is None:
        print("Sensor BME280 no inicializado. Saliendo del programa...")
        exit()
    # Create a logger instance
    logger = Logger()

    # Display initial sensor data
    time.sleep(2)
    print("Inicio del sistema de monitorización de energía\n")
    sendInit(bme280)

    # Validate GPIO pin setup
    validateGPIO(POWER_PIN)

    # Start the Flask server in a separate thread
    flask_thread = threading.Thread(target=flaskThread, daemon=True)
    flask_thread.start()

    # Monitor the power supply
    alarm_raised = False
    try:
        last_time = time.time()
        while True:
            showWeather(bme280)  # Display the weather data
            updateServerData(bme280, alarm_raised) # Update web infomation
            logger.log_data(server_data) # Log data to calculate averages
            
            if time.time() - last_time > 12:#DEP  # Log data every 20 minutes (1200 seconds)
                # Log data to CSV file
                logger.log_csv()
                last_time = time.time()
                print(f"[{time.strftime('%H:%M:%S')}] Data stored in the CSV file")

            # Check power status
            if GPIO.input(POWER_PIN) == GPIO.LOW:  # 0V = No power
                if not alarm_raised:
                    print("Nevera sin electricidad!")
                    sendAlert(bme280)
                    alarm_raised = True
            else:  # 3.3V = Power restored
                if alarm_raised:
                    print("El suministro eléctrico fue recuperado!")
                    sendRecovery(bme280)
                    alarm_raised = False

            time.sleep(POLLING_INTERVAL)

    except KeyboardInterrupt:
        print(f"[{time.strftime('%H:%M:%S')}] Script execution interrupted by user.")
    finally:
        GPIO.cleanup()
        print("Saliendo del programa: GPIO limpio correctamente.")
