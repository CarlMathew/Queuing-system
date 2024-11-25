from django.db import connection, Error
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def execute_query(query):
    cursor = connection.cursor()
    results = []
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row))for row in rows]
        return results
    except Error as err:
        print(f"Error:{err}")
    finally:
        cursor.close()
        connection.close()


def changeQuery(query):
    cursor= connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except Error as err: 
        print(f"Error:{err}")
    finally:
        cursor.close()
        connection.close()

def SendEmail(name, time, purpose):
    # email_Receive = "moradacarl2711@gmail.com"
    email_Receive = "nicochristopher0@gmail.com"
    Subject = "Missing RFID Card"
    message = MIMEMultipart()
    message["From"] = "monitorbroodingrearing@gmail.com"
    message["To"] = email_Receive
    message["Subject"] = Subject


    body = f"""
     Missing RFID Notification
     Name: {name}
     Time of Check In: {time}
     Purpose: {purpose}

    Please Don't Reply To this Email
    """

    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("monitorbroodingrearing@gmail.com", "nlxq wgth phof qjqf")
        text = message.as_string()
        server.sendmail("monitorbroodingrearing@gmail.com", email_Receive, text)
        print("Email Sent Successfully")
    except Error as err:
        print("Error: Email Sent Failed", Error)
    finally:
        server.quit()
