__author__ = 'Jincheul'

from .model import *

import pymysql
from pymysql.err import OperationalError

class DbManager():
    def __init__(self):
        # host = ""
        # user = ""
        # password = ""
        # dbName = ""
        # try:
        #     self.db_connector = pymysql.connect(host, user, password, dbName)
        #     self.isConnected = True
        # except OperationalError as e:
        #     self.isConnected = False
        pass

    def insert_user(self, user):
        is_inserted = False
        return is_inserted

    def update_user(self, user_name, password, email, mobile):
        is_updated = False
        return is_updated

    def delete_user(self, user_id, password):
        is_deleted = False;
        return is_deleted

    def get_user_type(self, user_id):
        return 'patient'

    def retrieve_patient(self, user_id, password=None):
        patient = {}
        # db_query = "SELECT * FROM user WHERE user_id=%s AND password=%s"
        # with self.mariadb_connector.cursor() as cursor:
        #     try:
        #         cursor.execute(db_query, (user_id, password))
        #         self.mariadb_connector.commit()
        #         for row in cursor:
        #             user.user_id = row[0]
        #             user.password = row[1]
        #     except Exception as e:
        #         return False
        # Dummy 'User'
        patient['id'] = 'min'
        patient['password'] = '1234'
        patient['user_name'] = 'Ah Young Min'
        patient['birth_date'] = '1992-10-18'
        patient['gender'] = 'Female'
        patient['mobile'] = '01045586587'
        patient['email'] = 'min1018@gmail.com'
        patient['join_date'] = '2015-12-17'
        patient['deactivate_date'] = None
        patient['user_type'] = 'patient'
        return patient

    def retrieve_patient_profile(self, user_id):
        patient_profile = PatientProfile()
        # Dummy 'profile'
        patient_profile.id = 'Patient_Profile_Min'
        patient_profile.height = 168
        patient_profile.weight = 59
        patient_profile.drink_capacity = 1
        patient_profile.dring_frequency = 2
        patient_profile.sleep_hour = 6
        patient_profile.exercise_hour = 0.5
        patient_profile.smoke_status = 'Nonesmoker'
        patient_profile.water_intake = 8
        patient_profile.disease_history = None
        patient_profile.medication = None
        patient_profile.family_histoy = 'Father: Heart Disease'
        patient_profile.significant = None
        patient_profile.notice = None
        return patient_profile

    def retrieve_physician(self, user_id):
        physician = Physician()
        # Dummy 'physician'
        physician.id = 'Physician_Han'
        physician.password = '1234'
        physician.user_name = 'Ye Hwa Han'
        physician.mobile = '01075681589'
        physician.email = 'han0818@gmail.com'
        physician.join_date = '2015-09-20'
        physician.deactivate_date = None
        physician.user_type = 'physician'
        physician.license_number = 'HIENLN23057AHEN-32HLKLKJ-KLKJ23'
        physician.major = 'Brain Specialist'
        physician.certificate_dir = ''
        return physician

    def retrieve_physician_profile(self):
        physician_profile = PhysicianProfile()
        # Dummy 'profile'
        physician_profile.id = 'Physician_Profile_Han'
        return physician_profile

    def retrieve_medical_image(self, user_id, upload_date):
        medical_image = MedicalImage()
        # Dummy 'medical_image'
        medical_image.id = 'Medical_Image_Min'
        medical_image.subject = 'ECG Image'
        medical_image.size = 20
        medical_image.type= 'ECG'
        medical_image.hospital = 'Seoul Hospital'
        medical_image.asmt_date = '2015-11-15'
        medical_image.upload_date = '2015-12-20'
        medical_image.exam_physician = 'Dr.Lee'
        medical_image.place = None
        medical_image.description = 'personal heart status'
        medical_image.comment = None
        return medical_image

    def retrieve_intpr(self, user_id):
        intpr = Interpretation()
        # Dummy 'interpretation'
        intpr.id = 'Interpretation_Min'
        intpr.level = 1
        intpr.fee = 'Free'
        intpr.date = '2016-01-08'
        intpr.summary = None
        intpr.status = None
        return intpr