import os, sys
# import png
import dicom
import mudicom
# import logging
# import pylab
# import matplotlib.pyplot as pyplot
import matplotlib.pylab as pylab
import gdcm

try:
    from PIL import Image
except ImportError:
    import Image

_testCompressedfile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2/IM-0001-0001.dcm"
_testDecompressedFile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2, DECOMP/IM-0001-0001.dcm"
_testImagedFile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2, PNG/IM-0001-0001.jpg"
_testImagedFile2 = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2, PNG/IM-0001-0001 2.jpg"

### show ###
# dFile = dicom.read_file(_testDecompressedFile)
# print dFile.file_meta
#
# pylab.imshow(dFile.pixel_array,cmap=pylab.cm.bone) # pylab readings and conversion
# pylab.show() #Dispaly


### to jpg ###
mufile = mudicom.load(_testDecompressedFile)
mufile.read()

# valdiation = mufile.validate()
# print valdiation

img = mufile.image
# img.numpy

img.save_as_plt(_testImagedFile)
