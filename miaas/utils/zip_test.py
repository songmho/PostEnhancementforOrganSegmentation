import os

import shutil
import zipfile

# from miaas.apis import logger


def _extract_zipfile(filename):
    zipfiledir = 'C:/Users/Khan/Desktop/ziptest'
    filename =zipfiledir+filename

    if os.path.exists(zipfiledir):
        shutil.rmtree(zipfiledir)
    with zipfile.ZipFile(filename, "r") as zfile:
        try:
            zfile.extractall(zipfiledir)
        except UnicodeDecodeError as e:
            _extractall_unicode(zfile, zipfiledir)

    sysfile_list = []
    for root, dirs, files in os.walk(zipfiledir):
        rootpath = os.path.abspath(root)
        for dir in dirs:
            dirpath = os.path.join(rootpath, dir)
            if dir.startswith('.') or dir.startswith('__'):
                sysfile_list.append(dirpath)
        for file in files:
            filepath = os.path.join(rootpath, file)
            if file.startswith('.') or file.startswith('__'):
                sysfile_list.append(filepath)

    for sysfile in sysfile_list:
        if not os.path.exists(sysfile):
            continue
        if os.path.isfile(sysfile):
            os.remove(sysfile)
        else:
            shutil.rmtree(sysfile)

    return zipfiledir


def _extractall_unicode(zf):
    for m in zf.infolist():
        data = zf.read(m)  # extract zipped data into memory
        # convert unicode file path to utf8
        disk_file_name = m.filename.encode('utf8')
        print(disk_file_name)
        dir_name = os.path.dirname(disk_file_name)
        print(dir_name)
        try:
            os.makedirs(dir_name)
        except OSError as e:
            if e.errno == os.errno.EEXIST:
                pass
            else:
                raise
        except Exception as e:
            raise

        with open(disk_file_name, 'wb') as fd:
            fd.write(data)
    zf.close()

if __name__ == '__main__':
    import dicom
    import os
    import numpy
    from matplotlib import pyplot, cm

    PathDicom = "C:/Users/Khan/Desktop/ziptest/WRIX/WRIST RIGHT/SCOUT 3-PLANE RT. - 2"
    lstFilesDCM = []  # create an empty list
    for dirName, subdirList, fileList in os.walk(PathDicom):
        for filename in fileList:
            if ".dcm" in filename.lower():  # check whether the file's DICOM
                lstFilesDCM.append(os.path.join(dirName,filename))

    # Get ref file
    RefDs = dicom.read_file(lstFilesDCM[0])

    # Load dimensions based on the number of rows, columns, and slices (along the Z axis)
    ConstPixelDims = (int(RefDs.Rows), int(RefDs.Columns), len(lstFilesDCM))

    # Load spacing values (in mm)
    ConstPixelSpacing = (float(RefDs.PixelSpacing[0]), float(RefDs.PixelSpacing[1]), float(RefDs.SliceThickness))


    x = numpy.arange(0.0, (ConstPixelDims[0]+1)*ConstPixelSpacing[0], ConstPixelSpacing[0])
    y = numpy.arange(0.0, (ConstPixelDims[1]+1)*ConstPixelSpacing[1], ConstPixelSpacing[1])
    z = numpy.arange(0.0, (ConstPixelDims[2]+1)*ConstPixelSpacing[2], ConstPixelSpacing[2])

    # The array is sized based on 'ConstPixelDims'
    ArrayDicom = numpy.zeros(ConstPixelDims, dtype=RefDs.pixel_array.dtype)

    # loop through all the DICOM files
    for filenameDCM in lstFilesDCM:
        # read the file
        ds = dicom.read_file(filenameDCM)
        # store the raw image data
        ArrayDicom[:, :, lstFilesDCM.index(filenameDCM)] = ds.pixel_array

    pyplot.figure(dpi=300)
    pyplot.axes().set_aspect('equal', 'datalim')
    pyplot.set_cmap(pyplot.gray())
    pyplot.pcolormesh(x, y, numpy.flipud(ArrayDicom[:, :, 80]))
