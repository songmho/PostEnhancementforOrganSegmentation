import smtplib
from email.mime.text import MIMEText
from . import constants


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

    def send_new_pwd(self, fir_name, last_name, email, new_pwd):
        try:

            msg = MIMEText('Hi '+fir_name+" "+last_name+"\n\n"+
                           "We heard that you lost MIAS account passowrd."+
                           "You can access your account using the following password:\n"+
                           new_pwd+"\n\n"+
                            "Thanks, \nThe MIAS Team")
            msg['Subject'] = "[MIAS] Please reset your password"

            self.session.sendmail(self.from_user, email, msg.as_string())

            self.session.quit()
            return True
        except:
            return False

    def send_activate_mail(self, fir_name, last_name, email, a_k):
        try:
            url = constants.HOST_ADDR+"/activate?email="+email+"&activation_key="+a_k
            msg = MIMEText('Hi '+fir_name+" "+last_name+"\n\n"+
                           "Thank you for signing up for the MIAS. We are really happy to meet you!"+
                           "In order to activate your account follow the "+
                            url+"\n\n"+
                            "Thanks, \nThe MIAS Team")
            msg['Subject'] = "[MIAS] Activation your account"

            self.session.sendmail(self.from_user, email, msg.as_string())

            self.session.quit()
            return True
        except:
            return False
