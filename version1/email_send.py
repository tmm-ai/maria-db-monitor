import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "anderson4ent@gmail.com"
receiver_email = "tom.m.mcnulty@gmail.com"
password = "svFkkKPv7ttveKZ046"

# Create the email headers and body
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = "Python Email Test"
body = "This is a test email sent from a Python script! - Yahoo!!"
message.attach(MIMEText(body, "plain"))

# Send the email
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, password)
    text = message.as_string()
    server.sendmail(sender_email, receiver_email, text)
    print("Email sent successfully")
except Exception as e:
    print(f"Error sending email: {e}")
finally:
    server.quit()
