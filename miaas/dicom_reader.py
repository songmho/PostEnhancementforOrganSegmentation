import os, sys
import dicom, mudicom, gdcm
import logging
# import matplotlib.pyplot as pyplot
import matplotlib.pylab as pylab
import time
import zipfile

_testCompressedfile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2/IM-0001-0001.dcm"
_testDecompressedFile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2, DECOMP/IM-0001-0001.dcm"
_testImagedFile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2, PNG/IM-0001-0001.jpg"
_testIconFile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2, PNG/IM-0001-0001-icon.jpg"

# def __init__():
#     print "init"
#
# def is_zipfile(archive_filename):
#     return zipfile.is_zipfile(archive_filename)
#
# def extract_dicom_archive(archive_filename):
#     if not is_zipfile(archive_filename): return False
#
#     # zfp = open(archive_filename, 'rb')
#     # zfile = zipfile.ZipFile(zfp)
#     with zipfile.ZipFile(archive_filename, "r") as zfile:
#         zfile.extractall()


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

# def plot_image(decomp_image):
#     dfile = dicom.read_file(decomp_image)
#     print dfile.file_meta
#
#     pylab.imshow(dfile.pixel_array, cmap=pylab.cm.bone) # pylab readings and conversion
#     pylab.show()

def convert_to_jpg(dcmfile, jpgfile):
    try:
        mufile = mudicom.load(dcmfile)
        mufile.read()

        img = mufile.image
        img.save_as_plt(jpgfile)
    except Exception as e:
        logging.exception(e)
        return False
    return True

if __name__ == "__main__":
    pass
    # decompress(_testCompressedfile, _testDecompressedFile)
    # convert_to_jpg(_testCompressedfile, _testImagedFile)
