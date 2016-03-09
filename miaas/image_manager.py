import os, shutil, glob
import datetime, time
import logging
import zipfile
from . import cloud_db, constants, dicom_reader

logging.basicConfig(
    format="[%(name)s][%(asctime)s] %(message)s",
    handlers=[logging.StreamHandler()],
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ImageManager():
    _temp_upload_dir = constants.TEMP_UPLOAD_DIR
    _supported_image_extensions = ['dicom', 'dcm', 'jpg', 'jpeg', 'png', 'zip']
    _supported_signal_extensions = ['csv', 'txt']

    def __init__(self, image_file, image_info):
        self._original_file = image_file
        self._temp_file_path = None
        self._image_info = image_info

    def upload_file(self):
        self.upload_as_temp()
        if not self._is_supported_file(self._temp_file_path):
            raise Exception("Unsupported File Extension.")
        temp_path = None
        if self._is_zipfile(self._temp_file_path):
            extract_dir = self._extract_zipfile(self._temp_file_path)
            success = self._dcm_to_jpg_indir(extract_dir)
            if not success:
                raise Exception("Invalid Dicom Image.")
            temp_path = extract_dir
        else:
            temp_path = self._temp_file_path
        logger.info('uploaded temp file: %s' % temp_path)

        self._upload_to_archive(temp_path)

    def update_file(self):
        pass

    def _upload_to_archive(self, temp_path):
        archive_path = os.path.join(constants.ARCHIVE_BASE_PATH,
                                    self._image_info['user_id'],
                                    self._image_info['image_type'],
                                    str(self._image_info['timestamp']))
        logger.info('archive path: %s' % archive_path)

        shutil.move(temp_path, archive_path)
        pass

    def _dcm_to_jpg_indir(self, dir):
        for root, dirs, files in os.walk(dir):
            rootpath = os.path.abspath(root)
            for file in files:
                if file.startswith('.') or file.startswith('__'):
                    continue
                dcmpath = os.path.join(rootpath, file)
                fileext = self._get_file_extension(dcmpath)
                if fileext not in ImageManager._supported_image_extensions:
                    return False
                if fileext=='dicom' or fileext=='dcm':
                    jpgpath = os.path.join(rootpath, '%s.jpg' % (os.path.splitext(file)[0]))
                    # logger.info('%s -> %s' % (dcmpath, jpgpath))
                    success = self._dcm_to_jpg(str(dcmpath), str(jpgpath))
                    if not success:
                        logger.info('dcm to jpg failed with: %s' % (file))
                        return False
                    os.remove(dcmpath)

        return True

    def _dcm_to_jpg(self, dcmfile, jpgfile):
        return dicom_reader.convert_to_jpg(dcmfile, jpgfile)

    def upload_as_temp(self):
        filename = self._original_file._name
        tempdir = '%s/%s/' % (constants.TEMP_UPLOAD_DIR, self._image_info['user_id'])
        try:
            if not os.path.exists(os.path.dirname(tempdir)):
                os.makedirs(os.path.dirname(tempdir))

            self._temp_file_path = '%s/%s' % (tempdir, filename)
            fp = open(self._temp_file_path, 'wb')
            for chunk in self._original_file.chunks():
                fp.write(chunk)
            fp.close()
            return True

        except Exception as e:
            logger.exception(e)
            return False

    def _is_zipfile(self, filename):
        return zipfile.is_zipfile(filename)

    def _extract_zipfile(self, filename):
        if not self._is_zipfile(filename):
            logger.info("it's not zipfile")
            return None
        zipfiledir = '%s/%s/' % (constants.TEMP_EXTRACT_DIR, self._image_info['user_id'])

        if os.path.exists(zipfiledir):
            shutil.rmtree(zipfiledir)
        with zipfile.ZipFile(filename, "r") as zfile:
            zfile.extractall(zipfiledir)

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

    def _is_supported_file(self, filepath):
        ext = self._get_file_extension(filepath)
        return ext in ImageManager._supported_image_extensions or \
               ext in ImageManager._supported_signal_extensions

    def _get_file_name(self, filepath):
        head, tail = os.path.split(filepath)
        return tail

    def _get_file_extension(self, filepath):
        filename = self._get_file_name(filepath)
        return filename.split(".")[-1].lower()


class ImageUploader():

    def __init__(self):
        self.cloud_instance_id = 'i-0aba2ecd'

    # i-0aba2ecd/min0532/ecg/20151127/min_ecg.dec
    def save_file(self, patient_id, type, file_name, image_file):
        file_name = ''
        dir = None
        now = datetime.datetime.now()
        res_date = str(now.year-1) + str(now.month) + str(now.day)
        file_path = 'G:\\' + self.cloud_instance_id + '\\' + patient_id + '\\' + type + '\\' + res_date
        try:
            # To check directory existence ,create relevant folders, and upload file to cloud EC2
            if not os.path.isdir(file_path):
                os.makedirs(file_path)
                dir = file_path
                file_name = dir + file_name
                destination = open(file_name, 'wb')
                for chunk in image_file.chunks():
                    destination.write(chunk)
                destination.close()
        except Exception as e:
            print("upload_file: ", e)

    def get_image(self, patient_id, subject):
        pass