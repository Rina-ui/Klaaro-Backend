import os
import smtplib
from email.message import EmailMessage

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "marinagracia895@gmail.com"
        self.sender_password = "wymrvqjfmxevxtae"

    def send_otp(self, to_email: str, firstname: str, code: str):
        msg = EmailMessage()
        msg['Subject'] = f"{code} est votre code de sécurité"
        msg['From'] = self.sender_email
        msg['To'] = to_email

        msg.set_content(f"""Bonjour {firstname},

Votre code de sécurité à 2 facteurs est :

    {code}

Ce code est valide pendant 5 minutes.
Si vous n'êtes pas à l'origine de cette demande, ignorez ce message.
""")

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)