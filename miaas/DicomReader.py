import os
import png
import dicom
import logging
# import pylab
import matplotlib.pyplot as pyplot
import matplotlib.pylab as pylab
from gdcmswig import *

try:
    from PIL import Image
except ImportError:
    import Image

dFile = dicom.read_file("/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2/IM-0001-0001.dcm")

pylab.imshow(dFile.pixel_array,cmap=pylab.cm.bone) # pylab readings and conversion
pylab.show() #Dispaly
