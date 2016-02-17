__author__ = 'Jincheul'

from cloud_db import *

class User():
    def __init__(self):
        self.id = None
        self.password = None
        self.name = None
        self.birth_date = None
        self.gender = None
        self.mobile = None
        self.email = None
        self.join_date = None
        self.deactivate_date = None

class Patient(User):
    def __init__(self):
        pass

    def get_patient_info(self, user_id):
        self.db_manager = DbManager()
        patient = self.db_manager.retrieve_patient(user_id)
        return patient

class PatientProfile():
    def __init__(self):
        self.id = None
        self.height = None
        self.weight = None
        self.drink_capacity = None
        self.dring_frequency = None
        self.sleep_hour = None
        self.exercise_hour = None
        self.smoke_status = None
        self.water_intake = None
        self.disease_history = None
        self.medication = None
        self.family_histoy = None
        self.significant = None
        self.notice = None

    def get_profile(self, user_id):
        self.db_manager = DbManager()
        profile = self.db_manager.retrieve_patient_profile(user_id)
        return profile

class Physician(User):
    def __init__(self):
        self.license_number = None
        self.major = None
        self.certificate_dir = None

    def get_physician_info(self, user_id):
        self.db_manager = DbManager()
        physician = self.db_manager.retrieve_physician(user_id)
        return physician

class PhysicianProfile():
    def __init__(self):
        self.id = None

    def get_profile(self,user_id):
        self.db_manager = DbManager()
        profile = self.db_manager.retrieve_physician_profile()
        return profile

class MedicalImage():
    def __init__(self):
        self.id = None
        self.subject = None
        self.size = None
        self.type = None
        self.hospital = None
        self.asmt_date = None #Assessment Date
        self.upload_date = None
        self.exam_physician = None
        self.place = None
        self.description = None
        self.comment = None

    def get_image(self, user_id, upload_date):
        self.db_manager = DbManager()
        image = self.db_manager.retrieve_medical_image(user_id, upload_date)
        return image

class Interpretation():
    def __init__(self):
        self.id = None
        self.level = None
        self.fee = None
        self.date = None
        self.summary = None
        self.status = None

    def get_interpretation(self, user_id):
        self.db_manager = DbManager()
        intpr = self.db_manager.retrieve_intpr(user_id)
        return intpr

if __name__ == '__main__':
    patient = Patient()
    patient = patient.get_patient_info('Patient_Min')
    print(patient.birth_date)

    patient_profile = PatientProfile()
    patient_profile = patient_profile.get_profile('Patient_Profile_Min')
    print(patient_profile.height)

    physician = Physician()
    physician = physician.get_physician_info('Physician_Han')
    print(physician.birth_date)

    physician_profile = PhysicianProfile()
    physician_profile = physician_profile.get_profile('Physician_Profile_Han')
    print(physician_profile.id)

    medical_image = MedicalImage()
    medical_image = medical_image.get_image('Patient_Min', '2015-01-01')
    print(medical_image.upload_date)

    intpr = Interpretation()
    intpr = intpr.get_interpretation('Interpretaion_Min')
    print(intpr.date)