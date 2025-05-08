# Home Watchdog Script
import smtplib
from email.message import EmailMessage
import time
import requests

# Configurable variables
POLLING_INTERVAL = 5  # Time to sleep in seconds between checks
EMAIL_RECIPIENTS = ["vicentedf88@gmail.com"]  # Add more recipients if needed
URL_WEBSITE = "http://chaletserreta.crabdance.com"  # URL public Raspberry Pi website
ZEROTIER_WEBSITE = "http://10.144.169.135:5000/"  # Local address of the Raspberry Pi website through ZeroTier

# Email credentials (hardcoded for now)
EMAIL_USER = "vicentedanvilaf@gmail.com"
EMAIL_PASSWORD = "ubjwhhbazadlmrii"  # Replace this with your application password of your Google account

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
def sendURLdown(url, html_error):
    local_time = time.localtime(time.time())
    time_string = time.strftime("%H:%M:%S, %d/%m/%Y", local_time)

    subject = f"🔴 La URL {url} no responde!"
    body = (
        f"¡La web {url} ha dejado de responder al watchdog a las {time_string}!\n"
        f"El error devuelto es: {html_error}\n\n"

        "Muchas gracias. Un saludo!"
    )

    for recipient in EMAIL_RECIPIENTS:
        emailAlert(subject, body, recipient)

    print("\tEmail de alerta por el corte de suministro enviado")
    print(f"\n\tAsunto: {subject}")
    print(f"\n\tCuerpo: {body}")

def get_error_explanation(status_code):
    explanations = {
        400: "Bad Request - The request was malformed.",
        401: "Unauthorized - Authentication required.",
        403: "Forbidden - Server is refusing the request.",
        404: "Not Found - The page/resource was not found.",
        408: "Request Timeout - The server timed out waiting for the request.",
        429: "Too Many Requests - You are being rate-limited.",
        500: "Internal Server Error - A generic server error.",
        502: "Bad Gateway - Received invalid response from upstream server.",
        503: "Service Unavailable - Server is down or overloaded.",
        504: "Gateway Timeout - Upstream server didn't respond in time.",
    }
    return explanations.get(status_code, "Unknown error - No specific explanation available.")

def check_website(url, web_ok):
    local_time = time.localtime(time.time())
    time_string = time.strftime("%H:%M:%S, %d/%m/%Y", local_time)

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"{time_string} - {url} is UP. Status code: {response.status_code}")
            return True
        else:
            explanation = get_error_explanation(response.status_code)
            print(f"{time_string} - {url} is DOWN. Status code: {response.status_code} - {explanation}")

            if web_ok:
                sendURLdown(url, f"{response.status_code} - {explanation}")
                web_ok = False
            return web_ok

    except requests.RequestException as e:
        print(f"{time_string} - {url} is DOWN. Exception: {e}")
        if web_ok:
            sendURLdown(url, f"RequestException - {str(e)}")
            web_ok = False
        return web_ok


if __name__ == "__main__":
    print("Iniciando watchdog...")
    url_web_ok = True
    zerotier_web_ok = True
    try:
        while True:
            # Check the availability of the URLs
            print("Comprobando la disponibilidad de las URLs...")
            url_web_ok = check_website(URL_WEBSITE, url_web_ok)
            zerotier_web_ok = check_website(ZEROTIER_WEBSITE, zerotier_web_ok)
            # Sleep for the specified polling interval
            time.sleep(POLLING_INTERVAL)

    except KeyboardInterrupt:
        print(f"[{time.strftime('%H:%M:%S')}] Script execution interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Saliendo del programa...")
