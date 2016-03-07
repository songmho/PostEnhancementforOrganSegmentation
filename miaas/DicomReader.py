import os, sys
# import png
# import dicom
# import logging
# import pylab
# import matplotlib.pyplot as pyplot
# import matplotlib.pylab as pylab
import gdcm

try:
    from PIL import Image
except ImportError:
    import Image

_testCompressedfile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2/IM-0001-0001.dcm"
_testDecompressedFile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2, DECOMP/IM-0001-0001.dcm"

file1 = _testCompressedfile
file2 = _testDecompressedFile

r = gdcm.ImageReader()
r.SetFileName( file1 )
if not r.Read():
    sys.exit(1)

image = gdcm.Image()
ir = r.GetImage()

image.SetNumberOfDimensions( ir.GetNumberOfDimensions() )
dims = ir.GetDimensions()
# print ir.GetDimension(0)
# print ir.GetDimension(1)
print "Dimensions:", dims, "\n"

#  Just for fun:
dircos = ir.GetDirectionCosines()
# t = gdcm.Orientation.GetType(dircos)
# print "Type:", t

# l = gdcm.Orientation.GetLabel(t)
# print "Orientation label:", l

# image.SetDimension(0, ir.GetDimension(0) )
# image.SetDimension(1, ir.GetDimension(1) )
image.SetDimension(0, dims[0])
image.SetDimension(1, dims[1])

pixeltype = ir.GetPixelFormat()
image.SetPixelFormat(pixeltype)
print "PixelFormat:\n", pixeltype

pi = ir.GetPhotometricInterpretation()
image.SetPhotometricInterpretation(pi)
print "PhotometricInterpretation:", pi, "\n"

str1 = ir.GetBuffer()
print len(str1)
print ir.GetBufferLength()
print "BufferLength:", len(str1), "\n"

pixeldata = gdcm.DataElement( gdcm.Tag(0x7fe0,0x0010) )
pixeldata.SetByteValue( str1, gdcm.VL( len(str1) ) )
image.SetDataElement( pixeldata )

w = gdcm.ImageWriter()
w.SetFileName( file2 )
w.SetFile( r.GetFile() )
w.SetImage( image )
if not w.Write():
    print "Write Error!"
    sys.exit(1)



# dFile = dicom.read_file("/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2/IM-0001-0001.dcm")
# pylab.imshow(dFile.pixel_array,cmap=pylab.cm.bone) # pylab readings and conversion
# pylab.show() #Dispaly

### show ###
dFile = dicom.read_file(_testDecompressedFile)
print dFile.file_meta

pylab.imshow(dFile.pixel_array,cmap=pylab.cm.bone) # pylab readings and conversion
pylab.show() #Dispaly


### to jpg ###
# mufile = mudicom.load(_testDecompressedFile)
# mufile.read()
#
# valdiation = mufile.validate()
# print valdiation
#
# img = mufile.image
# img.numpy
#
# img.save_as_plt(_testImagedFile)