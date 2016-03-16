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
    file_directory = '/home/sel/images/'
    file_name = 'ENTERIX.zip'

    if os.path.exists(file_directory):
        print "The directory exsits."
        with zipfile.ZipFile(file_directory+file_name) as zip_file:
            try:
                zip_file.extractall(file_directory)
            except UnicodeDecodeError as e:
                print e


    #
    # if os.path.exists(zipfiledir):
    #     shutil.rmtree(zipfiledir)
    # with zipfile.ZipFile(filename, "r") as zfile:
    #     try:
    #         zfile.extractall(zipfiledir)
    #     except UnicodeDecodeError as e:
    #         _extractall_unicode(zfile, zipfiledir)
    #
    # sysfile_list = []
    # for root, dirs, files in os.walk(zipfiledir):
    #     rootpath = os.path.abspath(root)
    #     for dir in dirs:
    #         dirpath = os.path.join(rootpath, dir)
    #         if dir.startswith('.') or dir.startswith('__'):
    #             sysfile_list.append(dirpath)
    #     for file in files:
    #         filepath = os.path.join(rootpath, file)
    #         if file.startswith('.') or file.startswith('__'):
    #             sysfile_list.append(filepath)
    #
    # for sysfile in sysfile_list:
    #     if not os.path.exists(sysfile):
    #         continue
    #     if os.path.isfile(sysfile):
    #         os.remove(sysfile)
    #     else:
    #         shutil.rmtree(sysfile)
    #
    # return zipfiledir
