import os
import datetime
from miaas.cloud_db import DbManager
import logging

logging.basicConfig(
    format="[%(name)s][%(asctime)s] %(message)s",
    handlers=[logging.StreamHandler()],
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ImageManager():
    def __init__(self, image_file, image_info):
        self.original_file = image_file
        self.image_info = image_info

    def upload_as_temp(self):
        filename = self.original_file._name
        tempdir = '%s/%s/' % ('./medical_images/temp/upload/', self.image_info['user_id'])
        try:
            if not os.path.exists(os.path.dirname(tempdir)):
                os.makedirs(os.path.dirname(tempdir))
            fp = open('%s/%s' % (tempdir, filename), 'wb')
            for chunk in self.original_file.chunks():
                fp.write(chunk)
            fp.close()
            return True

        except Exception as e:
            logger.exception(e)
            return False

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