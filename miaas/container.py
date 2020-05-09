from . import mias_smtp


class Container:
    s = mias_smtp.MailSender()

    def reset(self):
        self.s = None
        self.s = mias_smtp.MailSender()


mias_container = Container()
