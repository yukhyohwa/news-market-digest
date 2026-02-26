import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import config.settings as config

def send_report_email(report_path):
    """Sends the generated markdown report via Gmail SMTP."""
    if not os.path.exists(report_path):
        print(f"!!! Mail Error: Report file not found at {report_path}")
        return

    print(f">>> Attempting to send report via Email to {config.RECEIVER_EMAILS}...")

    # Read report content
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"!!! Mail Error: Failed to read report: {e}")
        return

    # Create Message
    message = MIMEMultipart()
    message['From'] = config.SENDER_EMAIL
    message['To'] = ", ".join(config.RECEIVER_EMAILS) # Display multiple in To header
    message['Subject'] = Header(f"Daily Arbitrage Report - {os.path.basename(report_path)}", 'utf-8')

    # Add content as plain text
    message.attach(MIMEText(content, 'plain', 'utf-8'))

    try:
        # Connect to Gmail SMTP (SSL)
        server = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT)
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        server.sendmail(config.SENDER_EMAIL, config.RECEIVER_EMAILS, message.as_string())
        server.quit()
        print(f">>> Success: Report sent to {len(config.RECEIVER_EMAILS)} recipients.")
    except Exception as e:
        print(f"!!! SMTP Error: {e}")
        print("Tip: Make sure you used a 16-digit 'App Password' and not your main account password.")
