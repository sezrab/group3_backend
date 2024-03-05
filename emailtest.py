import asyncio
from aiosmtpd import SMTP, Controller
import smtplib
from email.mime.text import MIMEText

# Define the local SMTP server class
class CustomSMTPHandler:
    async def handle_DATA(self, server, session, envelope):
        # Process the message (you can add custom handling here if needed)
        print(f"Received message from: {envelope.mail_from}")
        print(f"Recipients: {envelope.rcpt_tos}")
        print(f"Message data:\n{envelope.content.decode()}")

# Define function to send email
async def send_email():
    # Create SMTP server
    handler = CustomSMTPHandler()
    smtp_server = SMTP(handler)

    # Start the SMTP server
    controller = Controller(smtp_server)
    controller.start()

    # Create email message
    fromaddr = "nonexistent@example.com"
    toaddrs = ["recipient@example.com"]
    subject = "Test Email"
    body = "This is a test email sent from a non-existent address."
    msg = MIMEText(body)
    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddrs)
    msg['Subject'] = subject

    # Send the email
    try:
        smtp_client = smtplib.SMTP('localhost', controller.port)
        smtp_client.sendmail(fromaddr, toaddrs, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

    # Stop the SMTP server
    controller.stop()

# Run the send_email function
asyncio.run(send_email())
