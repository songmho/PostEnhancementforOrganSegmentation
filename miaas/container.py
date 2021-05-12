from . import mias_smtp
from miaas.lirads.software_process.main_process import LiradsProcess

class Container:
    lirads_process = LiradsProcess()
    s = mias_smtp.MailSender()

    def reset(self):
        self.s = None
        self.s = mias_smtp.MailSender()


mias_container = Container()
