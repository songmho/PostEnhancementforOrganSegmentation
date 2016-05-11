from django.core.mail import send_mail
from django.conf import settings
# mail install http://greenyant.blogspot.kr/2015/06/django-email.html
# MAC: sudo postfix start
# LINux: sudo apt-get install sendmail

def send_checking_mail():
    send_mail('Subject test', 'This is test email.', settings.EMAIL_DEFAULT_FROM,
              ['hanterkr@gmail.com'], fail_silently=False)
