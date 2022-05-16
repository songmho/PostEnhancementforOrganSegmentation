from . import mias_smtp
from miaas.lirads.software_process.main_process import LiradsProcess
from miaas.post_enhancement.post_process_v2 import PostEnhancement

class Container:
    post_enhancement_process = PostEnhancement()
    lirads_process = LiradsProcess()
    s = mias_smtp.MailSender()

    def reset(self):
        self.s = None
        self.s = mias_smtp.MailSender()


mias_container = Container()
