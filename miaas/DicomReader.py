import os, sys
# import png
import dicom
import mudicom
# import logging
# import matplotlib.pyplot as pyplot
import matplotlib.pylab as pylab
import gdcm
import time
# try:
#     from PIL import Image
# except ImportError:
#     import Image

_testCompressedfile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2/IM-0001-0001.dcm"
_testDecompressedFile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2, DECOMP/IM-0001-0001.dcm"
_testImagedFile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2, PNG/IM-0001-0001.jpg"
_testIconFile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2, PNG/IM-0001-0001-icon.jpg"

def run():
    decompress(_testCompressedfile, _testDecompressedFile)

def decompress(infile, outfile):
    r = gdcm.ImageReader()
    r.SetFileName(infile)
    if not r.Read():
        return False

    image = gdcm.Image()
    ir = r.GetImage()

    image.SetNumberOfDimensions(ir.GetNumberOfDimensions())
    dims = ir.GetDimensions()
    # print "Dimensions:", dims, "\n"
    image.SetDimension(0, dims[0])
    image.SetDimension(1, dims[1])

    pixeltype = ir.GetPixelFormat()
    image.SetPixelFormat(pixeltype)
    # print "PixelFormat:\n", pixeltype

    pi = ir.GetPhotometricInterpretation()
    image.SetPhotometricInterpretation(pi)
    # print "PhotometricInterpretation:", pi, "\n"

    buffer = ir.GetBuffer()
    # print "BufferLength:", len(buffer), "\n"
    pixeldata = gdcm.DataElement(gdcm.Tag(0x7fe0,0x0010))
    pixeldata.SetByteValue(buffer, gdcm.VL(len(buffer)))
    image.SetDataElement(pixeldata)

    w = gdcm.ImageWriter()
    w.SetFileName(outfile)
    w.SetFile(r.GetFile())
    w.SetImage(image)
    # w.SetPixmap(image)
    if not w.Write():
        print "Write Error!"
        return False
    return True

def plot_image(decomp_image):
    dfile = dicom.read_file(decomp_image)
    print dfile.file_meta

    pylab.imshow(dfile.pixel_array, cmap=pylab.cm.bone) # pylab readings and conversion
    pylab.show()

def convert_to_jpg(dcmfile, jpgfile):
    try:
        mufile = mudicom.load(dcmfile)
        mufile.read()

        img = mufile.image
        img.save_as_plt(jpgfile)
    except Exception:
        return False
    return True

if __name__ == "__main__":
    print "decompress start"
    # decompress(_testCompressedfile, _testDecompressedFile)
    print "decompress done"
    convert_to_jpg(_testDecompressedFile, _testImagedFile)
    # convert_to_jpg(_testDecompressedFile, _testImagedFile)
