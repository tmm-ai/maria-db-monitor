
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Your Yahoo account credentials
yahoo_user = 'interntom@yahoo.com'
yahoo_password = 'nqssbclqnyyqfdzo'  # Use an app password if 2FA is enabled

# Email details
recipient_email = 'tom.m.mcnulty@gmail.com'
subject = 'Test Email from Python'
body = 'This is a test email sent from Python using a Yahoo account!'

# Create MIME message
message = MIMEMultipart()
message['From'] = yahoo_user
message['To'] = recipient_email
message['Subject'] = subject
message.attach(MIMEText(body, 'plain'))

# Send the email via Yahoo's SMTP server
try:
    server = smtplib.SMTP('smtp.mail.yahoo.com', 587)  # Yahoo SMTP server address and port
    server.starttls()  # Upgrade the connection to secure
    server.login(yahoo_user, yahoo_password)  # Login to your Yahoo account
    text = message.as_string()  # Convert the message to string format
    server.sendmail(yahoo_user, recipient_email, text)  # Send the email
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
finally:
    server.quit()
