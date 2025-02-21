import smtplib
from email.mime.text import MIMEText
from app.config.settings import config

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = config.SMTP_USERNAME
    msg['To'] = to_email



    with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
        print("=========> 1")
        # with smtplib.SMTP("smtpidc.axisb.com", 2255) as server:
        # server.starttls()  # Start TLS encryption
        print("=========> 2")

        # server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        print(f"MSG: {msg}")
        # server.sendmail(msg.as_string())
        # server.sendmail("BRS.AutoMail@axisfinance.in", to_addrs="BRS.AutoMail@axisfinance.in", msg=msg.as_string())
        print("=========> 3")
        server.sendmail(config.SMTP_USERNAME, to_addrs=to_email, msg=msg.as_string())
        server.quit()
