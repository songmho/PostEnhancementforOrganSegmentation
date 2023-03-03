from . import mias_smtp
# from miaas.lirads.software_process.main_process import LiradsProcess
from miaas.post_enhancement.post_enhancement import MedImageEnhancer

class Container:
    post_enhancement_process = MedImageEnhancer()
mias_container = Container()
