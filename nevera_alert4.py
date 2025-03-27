#mkdir ~/bme280_project
#cd ~/bme280_project
#python3 -m venv venv
#source venv/bin/activate
#pip install adafruit-circuitpython-bme280
#pip install flask

import threading
from flask import Flask, jsonify, render_template_string
import RPi.GPIO as GPIO
import smtplib
from email.message import EmailMessage
import time
import board  # Don't use "pip install board", it's a different libraty from adafruit-blinka
from adafruit_bme280 import basic as adafruit_bme280  # pip install adafruit-circuitpython-bme280 (venv)

# Configurable variables
POLLING_INTERVAL = 1  # Time to sleep in seconds between checks
SEA_LEVEL_PRESSURE = 1016  # Pressure at sea level (Valencia, 16-12-2024)
POWER_PIN = 26  # GPIO pin used for power input monitoring
EMAIL_RECIPIENTS = ["vicentedf88@gmail.com"]  # Add more recipients if needed

# Email credentials (hardcoded for now)
EMAIL_USER = "vicentedanvilaf@gmail.com"
EMAIL_PASSWORD = "jbsksusietdizzlt"  # Replace this with your real password

# Flask setup
app = Flask(__name__)
server_data = {
    "temperature": None,
    "humidity": None,
    "pressure": None,
    "timestamp": None,
    "power_supply": "OFF"
}

@app.route('/')
def index():
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
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }
                h1 {
                    color: #4CAF50;
                    text-align: center;
                    font-size: 36px;
                    text-transform: uppercase;
                    margin-bottom: 30px;
                }
                p {
                    font-size: 18px;
                    margin: 10px 0;
                }
                strong {
                    color: #4CAF50;
                }
                .content {
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    max-width: 600px;
                    margin: 0 auto;
                }
                .timestamp {
                    font-size: 20px;
                    color: #777;
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
            </div>
        </body>
        </html>
    ''', **server_data)

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
    server_data["timestamp"] = time.strftime("%H:%M:%S, %d/%m/%Y")
    server_data["power_supply"] = "ON" if not power else "OFF"

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
        while True:
            showWeather(bme280)  # Display the weather data
            updateServerData(bme280, alarm_raised) #Update web infomation

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
