# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

# Program's email
PROGRAM_EMAIL = 'vidmngr@gmail.com'
PROGRAM_USERNAME = 'vidmngr'
PROGRAM_PASSWORD = 'Mov!esAndShows'

def SendEmail(to, subject, content, type='plain'):
	# Create a text/plain message
	msg = MIMEText(content, type)

	# me == the sender's email address
	# you == the recipient's email address
	msg['Subject'] = subject
	msg['From'] = PROGRAM_EMAIL
	msg['To'] = to
	# Send the message via our own SMTP server, but don't include the
	# envelope header.
	s = smtplib.SMTP('smtp.gmail.com:587')
	s.ehlo()
	s.starttls()
	s.login(PROGRAM_USERNAME, PROGRAM_PASSWORD)
	s.sendmail(PROGRAM_EMAIL, to, msg.as_string())
	s.quit()


if __name__ == "__main__":
    SendEmail('urishalit@gmail.com', 'VideoManager: Update', 'Hello!')