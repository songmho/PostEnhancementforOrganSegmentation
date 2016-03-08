__author__ = 'Jincheul'

import os
import datetime
from miaas.cloud_db import DbManager

class ImageUploader():

    def __init__(self):
        self.cloud_instance_id = 'i-0aba2ecd'

    # i-0aba2ecd/min0532/ecg/20151127/min_ecg.dec
    def save_file(self, patient_id, type, subject, image_file):
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
                file_name = dir + subject
                destination = open(file_name, 'wb')
                for chunk in image_file.chunks():
                    print('Chunk')
                    destination.write(chunk)
                destination.close()
        except Exception as e:
            print("upload_file: ", e)

    def get_image(self, patient_id, subject):
        pass