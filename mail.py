__author__ = 'Sean Yu'
'''created @2015/6/2''' 
# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

# Open a plain text file for reading.  For this example, assume that
# the text file contains only ASCII characters.

# Create a text/plain message
msg = MIMEText("hello")

# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = "test"
msg['From'] = 'sean.yu@calix.com'
msg['To'] = 'sean.yu@calix.com'

# Send the message via our own SMTP server, but don't include the
# envelope header.
s = smtplib.SMTP('localhost')
s.sendmail(me, [you], msg.as_string())
s.quit()