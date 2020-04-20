_testCompressedfile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2/IM-0001-0001.dcm"
_testDecompressedFile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2, DECOMP/IM-0001-0001.dcm"
_testImagedFile = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2, PNG/IM-0001-0001.jpg"
_testImagedFile2 = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2, PNG/IM-0001-0001 2.jpg"
_testFolder = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/"
_testFolder2 = "/Users/hanter/Downloads/dicom_ex/WRIX/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2"

import os, path, glob

print(os.listdir(_testFolder))
print(os.listdir(_testFolder2))

