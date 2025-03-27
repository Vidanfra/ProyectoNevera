import smtplib
from email.message import EmailMessage
import time

def email_alert(subject, body, to):
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

if __name__ == '__main__':
    local_time = time.localtime(time.time())
    time_string = time.strftime("%H:%M:%S, %d/%m/%Y", local_time)

    subject = "Nevera sin electricidad!"
    body =  "¡El suministro eléctrico en el chalet se ha cortado a las " + time_string + "!\nAcuda a rearmar el cuadro eléctrico antes de que la comida de la nevera se pudra y se llene de gusanos otra vez.\n\nMuchas gracias. Un saludo!"
    
    email_alert(subject, body, "vicentedf88@gmail.com")
    #email_alert(subject, body, "vicentedanvilacalatayud@gmail.com")
    #email_alert(subject, body, "vicentedanvila@gmail.com")

    print("Email de alerta enviado")
    print("\nAsunto: " + subject)
    print("\nCuerpo: "+ body)