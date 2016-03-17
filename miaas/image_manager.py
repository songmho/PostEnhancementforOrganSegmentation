import os, shutil, glob
import datetime, time
import logging
import subprocess
import zipfile, codecs
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
            # success = self._dcm_to_jpg_indir(extract_dir)
            # if not success:
            #     raise Exception("Invalid Dicom Image Format.")
            temp_path = extract_dir
        else:
            self.decompose(self._temp_file_path)
            temp_path = self._temp_file_path
        logger.info('uploaded temp file: %s' % temp_path)

        archive_path = self._upload_to_archive(temp_path)
        self.delete_temp_file()
        return archive_path

    def update_file(self):
        pass

    @classmethod
    def delete_uploaded_archive_file(cls, archive_path):
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

    def _dcm_to_jpg_indir(self, dir):
        for root, dirs, files in os.walk(dir):
            rootpath = os.path.abspath(root)
            for file in files:
                if file.startswith('.') or file.startswith('__'):
                    continue
                dcmpath = os.path.join(rootpath, file)
                fileext = self._get_file_extension(dcmpath)
                if fileext not in ImageManager._supported_image_extensions:
                    logger.info('not supoorted image extension: %s' % file)
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

    def decompose(self, filepath):
        p = subprocess.Popen(['sudo', 'python', './decompose.py', filepath.encode('ascii','ignore')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.stdin.write("'" + '\n')
        p.stdin.close()
        for line in p.stdout.readlines():
            logger.info(line)
        p.wait()


    def _is_zipfile(self, filename):
        return zipfile.is_zipfile(filename)

    #extract zipfiles
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

        #find sysfiles
        sysfile_list = []
        for root, dirs, files in os.walk(zipfiledir):
            rootpath = os.path.abspath(root)
            for dir in dirs:
                dirpath = os.path.join(rootpath, dir)
                if dir.startswith('.') or dir.startswith('__'):
                    sysfile_list.append(dirpath)
            for file in files:
                filepath = os.path.join(rootpath, file)
                # logger.info("################################################3")
                # logger.info('/home/sel/MIaaS/src/miaas/decompose.py'+ str(filepath))
                # logger.info(os.getcwd())
                self.decompose(filepath)

                if file.startswith('.') or file.startswith('__'):
                    sysfile_list.append(filepath)

        #remove sysfiles
        for sysfile in sysfile_list:
            if not os.path.exists(sysfile):
                continue
            if os.path.isfile(sysfile):
                os.remove(sysfile)
            else:
                shutil.rmtree(sysfile)

        #remove invalid dicom files

        return zipfiledir

    def _extractall_unicode(self, zf, extractdir):
        for m in zf.infolist():
            data = zf.read(m) # extract zipped data into memory
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
        return ext in ImageManager._supported_image_extensions or \
               ext in ImageManager._supported_signal_extensions

    def _get_file_name(self, filepath):
        head, tail = os.path.split(filepath)
        return tail

    def _get_file_extension(self, filepath):
        filename = self._get_file_name(filepath)
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
