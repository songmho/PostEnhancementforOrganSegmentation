import os, shutil, glob
import datetime, time
import logging
import subprocess
import zipfile, codecs
import dicom
from miaas.utils import edf_to_csv
from . import cloud_db, constants, dicom_reader

logging.basicConfig(
    format="[%(name)s][%(asctime)s] %(message)s",
    handlers=[logging.StreamHandler()],
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class ImageManager():
    _temp_upload_dir = constants.TEMP_UPLOAD_DIR
    _supported_image_extensions = ['dcm', 'jpg', 'jpeg', 'png', 'zip']
    _supported_signal_extensions = ['csv', 'edf']
    _supported_multi_extensions = ['dcm', 'jpg', 'jpeg', 'png']

    def __init__(self, image_files, image_info):
        self._original_files = image_files
        self._temp_file_path = None
        self._image_info = image_info
        self._is_mutliple_file = False

    def upload_file(self):
        self.upload_as_temp()
        temp_path = None
        if self._is_mutliple_file:
            temp_path = self._temp_file_path
        else:
            if not self._is_supported_file(self._temp_file_path):
                raise Exception("Unsupported File Extension.")

            if self._is_zipfile(self._temp_file_path):
                extract_dir = self._extract_zipfile(self._temp_file_path)
                temp_path = extract_dir
            else:
                temp_path = self._temp_file_path
                temp_path_ext = self._get_file_extension(temp_path)
                if temp_path_ext == 'dcm':
                    self.decompose(self._temp_file_path)
                if temp_path_ext == 'csv':
                    pass
                    # temp_path = self.csv_reorganize(self._temp_file_path)
                elif temp_path_ext == 'edf':
                    temp_path = edf_to_csv.edf_to_csv(temp_path)

        logger.info('uploaded temp file: %s' % temp_path)
        archive_path = self._upload_to_archive(temp_path)

        self.delete_temp_file()
        self.delete_file(temp_path)
        return archive_path

    def update_file(self):
        pass

    @classmethod
    def delete_file(cls, archive_path):
        try:
            if os.path.exists(archive_path):
                if os.path.isfile(archive_path):
                    os.remove(archive_path)
                elif os.path.isdir(archive_path):
                    shutil.rmtree(archive_path)
        except:
            pass

    def delete_temp_file(self):
        try:
            if os.path.exists(self._temp_file_path):
                os.remove(self._temp_file_path)
                self._temp_file_path = None
        except:
            pass

    def _upload_to_archive(self, temp_path):
        archive_root = os.path.join(constants.ARCHIVE_BASE_PATH,
                                    self._image_info['user_id'],
                                    self._image_info['image_type'])
        archive_path = os.path.join(archive_root,
                                    str(self._image_info['timestamp']))
        if os.path.isfile(temp_path):
            archive_path = '%s.%s' % (archive_path, self._get_file_extension(temp_path))
        logger.info('archive path: %s' % archive_path)

        if not os.path.exists(archive_root):
            os.makedirs(str(archive_root) + '/')

        shutil.move(temp_path, archive_path)
        return archive_path

    def upload_as_temp(self):
        if len(self._original_files) <= 0:
            raise Exception('No files')
        elif len(self._original_files) == 1:
            filename = self._original_files[0]._name
            tempdir = '%s/%s/' % (constants.TEMP_UPLOAD_DIR, self._image_info['user_id'])
            try:
                if not os.path.exists(os.path.dirname(tempdir)):
                    os.makedirs(os.path.dirname(tempdir))

                self._temp_file_path = '%s/%s' % (tempdir, filename)
                fp = open(self._temp_file_path, 'wb')
                for chunk in self._original_files[0].chunks():
                    fp.write(chunk)
                fp.close()
                return True

            except Exception as e:
                logger.exception(e)
                raise Exception('Uploading file failed.')
                return False

        else:
            self._is_mutliple_file = True
            first_ext = self._get_file_extension(self._original_files[0]._name)
            if first_ext not in self._supported_multi_extensions:
                raise Exception('These files are cannot upload multiply.')
            for file in self._original_files:
                ext = self._get_file_extension(file._name)
                logger.info(ext)
                if first_ext != ext:
                    raise Exception('These files are not same extension files.')

            userdir = '%s/%s' % (constants.TEMP_UPLOAD_DIR, self._image_info['user_id'])
            tempfolder = '%s/%s' % (userdir, 'upload')
            self._temp_file_path = tempfolder
            try:
                if not os.path.exists(userdir):
                    os.makedirs(userdir)

                logger.info(tempfolder)
                if os.path.exists(tempfolder):
                    shutil.rmtree(tempfolder)
                os.makedirs(tempfolder)

                for file in self._original_files:
                    filepath = '%s/%s' % (tempfolder, file._name)
                    fp = open(filepath, 'wb')
                    for chunk in file.chunks():
                        fp.write(chunk)
                    fp.close()
                return True

            except Exception as e:
                logger.exception(e)
                raise Exception('Uploading file failed.')
                return False

    def decompose(self, filepath):
        try:
            p = subprocess.Popen(['sudo', 'python', './decompose.py', filepath.encode('ascii','ignore')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            p.stdin.write("'" + '\n')
            p.stdin.close()
            # for line in p.stdout.readlines():
            #     logger.info(line)
            p.wait()
        except Exception as e:
            logger.exception(e)
            pass

    # reorganize csv table structure for header, time, and etc
    def csv_reorganize(self, filepath):
        import csv

        dirname, filename = os.path.split(filepath)
        # name_n_ext = filename.split(".")
        newpath = dirname + '/n_' + filename

        print ('filename %s -> %s' % (filepath, newpath))

        with open(filepath, 'rb') as orifile, open(newpath, 'wb') as newfile:
            csv_reader = csv.reader(orifile, delimiter=',', quotechar='|')
            csv_writer = csv.writer(newfile, delimiter=',', quotechar='|')

            header_row = csv_reader.next()
            if not header_row:
                raise Exception('There are no row.')

            header_len = len(header_row)
            if header_len <= 1:
                raise Exception('Too less column. There is no time or value column.')
            if header_len == 2 and header_row[1].strip().lower().startswith('time'):
                raise Exception('There is no value column.')

            time_column_pos = -1
            for i in range(0, 2):
                if header_row[i].strip().lower().startswith('time'):
                    time_column_pos = i
                    break

            if time_column_pos == -1:
                time_column_pos = 0
                header_row[0] = 'Time'

            first_row = csv_reader.next()
            if not first_row:
                raise Exception('There are no data rows.')
            second_row = csv_reader.next()
            if not first_row:
                raise Exception('There are too few data rows.')

            # if header_row[time_column_pos].strip().lower() == 'time':
            if header_row[time_column_pos].strip().lower().startswith('time'):
                first_time = float(first_row[time_column_pos])
                second_time = float(second_row[time_column_pos])
                print ('first: %s, second: %s' % (first_time, second_time))

                if (first_time == 0 or first_time == 1) and (first_time+1 == second_time):
                    header_row[time_column_pos] = 'Time (count)'
                elif (first_time < 1) and (second_time-first_time < 1):
                    header_row[time_column_pos] = 'Time (second)'
                elif (first_time > 0) and (first_time < 1000):
                    header_row[time_column_pos] = 'Time (ms)'
                elif first_time >= 100000:     # timestamp
                    header_row[time_column_pos] = 'Time (datetime)'
                elif first_time < -1:
                    header_row[time_column_pos] = 'Time (datetime)'
                else:
                    header_row[time_column_pos] = 'Time'

            csv_writer.writerow(header_row[time_column_pos:])
            csv_writer.writerow(first_row[time_column_pos:])
            csv_writer.writerow(second_row[time_column_pos:])
            print ', '.join(header_row[time_column_pos:])
            print '------------------'
            print ', '.join(first_row[time_column_pos:])
            print ', '.join(second_row[time_column_pos:])
            for row in csv_reader:
                print ', '.join(row[time_column_pos:])
                csv_writer.writerow(row[time_column_pos:])

        # return newpath
        return newpath


    def _is_zipfile(self, filename):
        return zipfile.is_zipfile(filename)

    # extract zipfiles
    def _extract_zipfile(self, filename):
        if not self._is_zipfile(filename):
            logger.info("it's not zipfile")
            return None
        zipfiledir = '%s/%s/' % (constants.TEMP_EXTRACT_DIR, self._image_info['user_id'])
        if os.path.exists(zipfiledir):
            shutil.rmtree(zipfiledir)
        with zipfile.ZipFile(filename, "r") as zfile:
            try:
                zfile.extractall(zipfiledir)
            except UnicodeDecodeError as e:
                self._extractall_unicode(zfile, zipfiledir)

        # find sysfiles and check the file is dicom file
        sysfile_list = []
        is_there_dicom = True
        first_file_ext = None
        supported_files = False
        for root, dirs, files in os.walk(zipfiledir):
            rootpath = os.path.abspath(root)

            # for remove sysfiles
            for dir in dirs:
                dirpath = os.path.join(rootpath, dir)
                if dir.startswith('.') or dir.startswith('__'):
                    sysfile_list.append(dirpath)

            # remove invalid dicom files
            # and add *.dcm file extension
            for file in files:
                filepath = os.path.join(rootpath, file)

                # for remove sysfiles
                if file.startswith('.') or file.startswith('__'):
                    sysfile_list.append(filepath)
                    continue

                file_ext = self._get_file_extension(filepath)
                if first_file_ext is None:
                    first_file_ext = file_ext

                if file_ext != first_file_ext:
                    raise Exception('The files in zip are not same extension files.')
                elif file_ext is None:
                    # check dicom file and add *.dcm extension
                    try:
                        dicom_file = dicom.read_file(filepath)
                        if len(dicom_file.pixel_array):
                            supported_files = True
                            os.rename(filepath, filepath+'.dcm')
                            self.decompose(filepath+'.dcm')
                        else:
                            # remove invalid dicom files
                            os.remove(filepath)
                            continue
                    except Exception as e:
                        os.remove(filepath)
                        logger.info(e)
                        continue
                elif file_ext == 'dicom':
                    supported_files = True
                    dcmpath = filepath.replace('.dicom', '.dcm')
                    os.rename(filepath, dcmpath)
                    self.decompose(dcmpath)
                elif file_ext not in self._supported_multi_extensions:
                    raise Exception('The files in zip are cannot upload multiply. '
                                    'The zip file only contains *.jpg, *.png, *.dcm.')
                else:
                    # common image files (jpg, png, dcm)
                    if file_ext == 'dcm':
                        print ('decompose %s' % filepath)
                        self.decompose(filepath)
                    supported_files = True
                    pass

                # logger.info("################################################3")
                # logger.info('/home/sel/MIaaS/src/miaas/decompose.py'+ str(filepath))
                # logger.info(os.getcwd())



        if not supported_files:
            raise Exception("The zip file doesn't contain supported files.")

        #remove sysfile
        for sysfile in sysfile_list:
            if not os.path.exists(sysfile):
                continue
            if os.path.isfile(sysfile):
                os.remove(sysfile)
            else:
                shutil.rmtree(sysfile)

        return zipfiledir

    def _extractall_unicode(self, zf, extractdir):
        for m in zf.infolist():
            data = zf.read(m)  # extract zipped data into memory
            # convert unicode file path to utf8
            disk_file_name = m.filename.encode('utf8')
            dir_name = os.path.dirname(disk_file_name)
            try:
                os.makedirs(dir_name)
            except OSError as e:
                logger.exception(e)
                if e.errno == os.errno.EEXIST:
                    pass
                else:
                    raise
            except Exception as e:
                logger.exception(e)
                raise

            with open(disk_file_name, 'wb') as fd:
                fd.write(data)
        zf.close()

    def _is_supported_file(self, filepath):
        ext = self._get_file_extension(filepath)
        if ext == None:
            return False
        return ext in ImageManager._supported_image_extensions or \
               ext in ImageManager._supported_signal_extensions

    def _get_file_name(self, filepath):
        head, tail = os.path.split(filepath)
        return tail

    def _get_file_extension(self, filepath):
        filename = self._get_file_name(filepath)
        if filename.find(".") < 0:
            return None
        return filename.split(".")[-1].lower()


class ImageRetriever():
    @classmethod
    def get_image_list(cls, image_dir):
        image_list = {}
        file_name = cls._get_file_name(image_dir)
        image_list[file_name] = cls._make_image_info_dict(image_dir)
        return image_list

    @classmethod
    def _make_image_info_dict(cls, filepath):
        image_info = {}
        if os.path.isfile(filepath):
            image_info['type'] = cls._get_file_extension(filepath)
            image_info['dir'] = filepath
        else:
            image_info['type'] = 'folder'
            file_list = os.listdir(filepath)
            image_info['file_list'] = {}
            for filename in file_list:
                if filename.startswith('.') or filename.startswith('__'):
                    continue
                image_info['file_list'][filename] = \
                    cls._make_image_info_dict(os.path.join(filepath, filename))
        # image_info['dir'] = filepath
        return image_info

    @classmethod
    def _is_file(cls, filepath):
        return os.path.isfile(filepath)

    @classmethod
    def _get_file_name(self, filepath):
        head, tail = os.path.split(filepath)
        return tail

    @classmethod
    def _get_file_extension(cls, filepath):
        filename = cls._get_file_name(filepath)
        return filename.split(".")[-1].lower()
