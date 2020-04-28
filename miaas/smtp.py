import smtplib
from email.mime.text import MIMEText

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

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

    def send_new_pwd(self, fir_name, last_name, email, u_id):
        try:
            id = urlsafe_base64_encode(force_bytes(u_id))
            email_encode = urlsafe_base64_encode(force_bytes(email))
            url = "http://"+constants.HOST_ADDR+"/change_password/"+id+"/"+email_encode
            msg = MIMEText('Hi '+fir_name+" "+last_name+"\n\n"+
                           "We heard that you lost MIAS account passowrd."+
                           "You can change your password using the following link: \n"+
                           url+"\n\n"+
                            "Thanks, \nThe MIAS Team")
            msg['Subject'] = "[MIAS] Please reset your password"

            self.session.sendmail(self.from_user, email, msg.as_string())

            self.session.quit()
            return True
        except:
            return False

    def send_activate_mail(self, fir_name, last_name, email, u_id, key):
        try:
            id = urlsafe_base64_encode(force_bytes(u_id))
            url = "http://"+constants.HOST_ADDR+"/activate/"+id+"/"+key
            # url = "http://127.0.0.1:8000/"+"/activate?email="+id+"&activation_key="+key
            msg = MIMEText('Hi '+fir_name+" "+last_name+"\n\n"+
                           "Thank you for signing up for the MIAS. We are really happy to meet you!"+
                           "In order to activate your account using the following link: "+
                            url+"\n\n"+
                            "Thanks, \nThe MIAS Team")
            msg['Subject'] = "[MIAS] Activation your account"

            self.session.sendmail(self.from_user, email, msg.as_string())

            self.session.quit()
            return True
        except:
            return False

if __name__ == '__main__':
    ms = MailSender()
    print(ms.send_activate_mail("test", "test", "songmho@gmail.com", 3, "Test"))