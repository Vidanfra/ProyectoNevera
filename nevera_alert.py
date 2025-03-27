import RPi.GPIO as GPIO
import smtplib
from email.message import EmailMessage
import time

def emailAlert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = "vicentedanvilaf@gmail.com"
    msg['from'] = user
    password = "jbsksusietdizzlt" #"emailalert1234"

    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)

    server.quit()

def sendAlert():
    local_time = time.localtime(time.time())
    time_string = time.strftime("%H:%M:%S, %d/%m/%Y", local_time)

    subject = "Nevera sin electricidad!"
    body =  "¡El suministro eléctrico en el chalet se ha cortado a las " + time_string + "!\nAcuda a rearmar el cuadro eléctrico antes de que la comida de la nevera se pudra y se llene de gusanos otra vez.\n\nMuchas gracias. Un saludo!"
    
    emailAlert(subject, body, "vicentedf88@gmail.com")
    #emailAlert(subject, body, "vicentedanvilacalatayud@gmail.com")
    #emailAlert(subject, body, "vicentedanvila@gmail.com")

    print("\tEmail de alerta enviado")
    print("\n\tAsunto: " + subject)
    print("\n\tCuerpo: "+ body)

if __name__ == '__main__':

    print("Iniciando...")

    # Set Pin Numbering to GPIO.BCM or GPIO.BOARD
    GPIO.setmode(GPIO.BCM)
    # Set Pin Number
    powerIn = 26
    # Set powerIn as input and set the initial value to zero
    GPIO.setup(powerIn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # Initial status of the alarm
    alarm_raised = False

    time.sleep(2)
    print("Inicio del sistema de monitorización de energía\n")

    try:
        while True:
            if(GPIO.input(powerIn) == False): # 0V in the digital input
                if(alarm_raised == False):
                    print("Nevera sin electricidad!")
                    sendAlert()
                    alarm_raised = True
                
            else:                   # 3.3V in the digital input
                if(alarm_raised == True):
                    print("El suministro eléctrico fue recuperado!")
                    alarm_raised = False

            time.sleep(1)
    except KeyboardInterrupt:
        print('Script execution interrupted by user')
    finally:		
        GPIO.cleanup()
        print('Exiting execution: cleanning GPIO setup')          