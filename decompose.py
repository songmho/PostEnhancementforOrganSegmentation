import gdcm

import sys


def decompose(filepath):
    r = gdcm.ImageReader()
    r.SetFileName(filepath)
    if not r.Read():
        raise Exception("No file.")

    image = gdcm.Image()
    ir = r.GetImage()

    image.SetNumberOfDimensions( ir.GetNumberOfDimensions() )
    dims = ir.GetDimensions()

    image.SetDimension(0, ir.GetDimension(0))
    image.SetDimension(1, ir.GetDimension(1))
    pixeltype = ir.GetPixelFormat()
    image.SetPixelFormat(pixeltype)

    pi = ir.GetPhotometricInterpretation()
    image.SetPhotometricInterpretation(pi)

    pixeldata = gdcm.DataElement(gdcm.Tag(0x7fe0, 0x0010))
    str1 = ir.GetBuffer()
    pixeldata.SetByteValue(str1, gdcm.VL(len(str1)))
    image.SetDataElement(pixeldata)

    w = gdcm.ImageWriter()
    w.SetFileName(filepath)
    w.SetFile(r.GetFile())
    w.SetImage(image)
    if not w.Write():
        raise Exception("Write failed.")
    w = None

if __name__ == '__main__':
    decompose(sys.argv[1])

