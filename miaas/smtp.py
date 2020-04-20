import smtplib
from email.mime.text import MIMEText


class MailSender:
    def __init__(self):
        self.from_user = "mias.selab@gmail.com"
        self.session = smtplib.SMTP("smtp.gmail.com", 587)
        self.session.starttls()
        self.session.login(self.from_user, "coplupgxuapzywuk")

    def send_mail(self, fir_name, last_name, email, list_role, invite_code):
        try:

            roles = ', '.join(list_role)
            msg = MIMEText('Dear '+fir_name+" "+last_name+"\n\n"+"You are invited at BOKAS as "+roles+".\n "+
                           "And you can use the following invitation Code.\n"+invite_code+".\n\nEnjoy BOKAS!")
            msg['Subject'] = "BOKAS - Invitation Mail"

            self.session.sendmail(self.from_user, email, msg.as_string())

            self.session.quit()
            return True
        except:
            return False
