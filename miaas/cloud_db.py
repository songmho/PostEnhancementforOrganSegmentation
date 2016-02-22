__author__ = 'Jincheul'


import pymysql

class DbManager():
    def __init__(self):
        host = 'rainbowdb.czg2t6iatylv.us-west-2.rds.amazonaws.com'
        user = 'root'
        port = 3306
        password = 'lovejesus'
        dbName = 'miaas'
        try:
            self.connector = pymysql.connect(host=host, port=port, user=user, passwd=password, db=dbName)
            self.is_connected = True
        except Exception as e:
            print(e)
            self.is_connected = False

    def add_patient(self, patient):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add patient information to 'patient' table
                db_query = "INSERT INTO patient values ()"
                cursor.execute(db_query, ())
                self.connector.commit()
                row_id = cursor.lastrowid
                # Add patient information to 'user' table
                password = patient['password']
                user_type = patient['user_type']
                name = patient['name']
                gender = patient['gender']
                birth_date = patient['birth_date']
                mobile = patient['mobile']
                email = patient['email']
                join_date = patient['join_date']
                deactivate_date = patient['deactivate_date']
                db_query = "INSERT INTO user (password, user_type, name, gender, birth_date, mobile, email, join_date, deactivate_date, patient_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query, (password, user_type, name, gender, birth_date, mobile, email, join_date, deactivate_date, row_id))
                self.connector.commit()
                row_id = cursor.lastrowid
                if row_id > 0:
                    if_inserted = True
            except Exception as e:
                print("Exception: ", e)
            finally:
                self.connector.close()
                return if_inserted

    def retrieve_patient(self, patient_id):
        user = {}
        db_query = "SELECT u.password, u.user_type, u.name, u.gender, u.birth_date, u.mobile, u.email, u.join_date, u.deactivate_date FROM patient as p LEFT JOIN user as u on p.patient_id=u.patient_id WHERE p.patient_id=%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (patient_id))
                self.connector.commit()
                for row in cursor:
                    user['patient_id'] = patient_id
                    user['password'] = row[0]
                    user['user_type'] = row[1]
                    user['name'] = row[2]
                    user['gender'] = row[3]
                    user['birth_date'] = row[4]
                    user['mobile'] = row[5]
                    user['email'] = row[6]
                    user['join_date'] = row[7]
                    user['deactivate_date'] = row[8]
            except Exception as e:
                print("Exception: ", e)
            finally:
                self.connector.close()
        return user

    def add_patient_profile(self, profile):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add patient profile to 'patient_profile' table
                patient_id = profile['patient_id']
                height = profile['height']
                weight = profile['weight']
                drink_capacity = profile['drink_capacity']
                drink_frequency = profile['drink_frequency']
                sleep_hour = profile['sleep_hour']
                exercise_hour = profile['exercise_hour']
                smoke_status = profile['smoke_status']
                water_intake = profile['water_intake']
                disease_history = profile['disease_history']
                medication = profile['medication']
                family_history =profile['family_history']
                significant = profile['significant']
                notice = profile['notice']
                db_query = "INSERT INTO patient_profile (patient_id, height, weight, drink_capacity, drink_frequency, sleep_hour, exercise_hour, smoke_status, water_intake, disease_history, medication, family_history, significant, notice) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query, (patient_id, height, weight, drink_capacity, drink_frequency, sleep_hour, exercise_hour, smoke_status, water_intake, disease_history, medication, family_history, significant, notice))
                self.connector.commit()
                row_id = cursor.lastrowid
                if row_id > 0:
                    if_inserted = True
            except Exception as e:
                print("Exception: ", e)
            finally:
                self.connector.close()
                return if_inserted

    def retrieve_patient_profile(self, patient_id, time_from=None):
        profiles = []
        date = int(time_from) if time_from is not None else 0
        db_query = "SELECT * FROM patient_profile WHERE patient_id=%s and timestamp>%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (patient_id, date))
                self.connector.commit()
                profile = {}
                for row in cursor:
                    profile['patient_profile_id'] = row[0]
                    profile['patient_id'] = row[1]
                    profile['height'] = row[2]
                    profile['weight'] = row[3]
                    profile['drink_capacity'] = row[4]
                    profile['drink_frequency'] = row[5]
                    profile['sleep_hour'] = row[6]
                    profile['exercise_hour'] = row[7]
                    profile['smoke_status'] = row[8]
                    profile['water_intake'] = row[9]
                    profile['disease_history'] = row[10]
                    profile['medication'] = row[11]
                    profile['family_history'] = row[12]
                    profile['significant'] = row[13]
                    profile['notice'] = row[14]
                    profiles.append(profile)
            except Exception as e:
                print("Exception: ", e)
            finally:
                self.connector.close()
        return profiles

    def add_physician(self, physician):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add patient information to 'physician' table
                license_number = physician['license_number']
                major = physician['major']
                certificate_dir = physician['certificate_dir']
                db_query = "INSERT INTO physician (license_number, major, certificate_dir) values (%s, %s, %s)"
                cursor.execute(db_query, (license_number, major, certificate_dir))
                self.connector.commit()
                row_id = cursor.lastrowid
                # Add physician information to 'user' table
                password = physician['password']
                user_type = physician['user_type']
                name = physician['name']
                gender = physician['gender']
                birth_date = physician['birth_date']
                mobile = physician['mobile']
                email = physician['email']
                join_date = physician['join_date']
                deactivate_date = physician['deactivate_date']
                db_query = "INSERT INTO user (password, user_type, name, gender, birth_date, mobile, email, join_date, deactivate_date, physician_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query, (password, user_type, name, gender, birth_date, mobile, email, join_date, deactivate_date, row_id))
                self.connector.commit()
                row_id = cursor.lastrowid
                if row_id > 0:
                    if_inserted = True
            except Exception as e:
                print("Exception: ", e)
            finally:
                self.connector.close()
                return if_inserted

    def retrieve_physician(self, physician_id):
        user = {}
        db_query = "SELECT u.password, u.user_type, u.name, u.gender, u.birth_date, u.mobile, u.email, u.join_date, u.deactivate_date, p.license_number, p.major, p.certificate_dir FROM physician as p LEFT JOIN user as u on p.physician_id=u.physician_id WHERE p.physician_id=%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (physician_id))
                self.connector.commit()
                for row in cursor:
                    user['physician_id'] = physician_id
                    user['password'] = row[0]
                    user['user_type'] = row[1]
                    user['name'] = row[2]
                    user['gender'] = row[3]
                    user['birth_date'] = row[4]
                    user['mobile'] = row[5]
                    user['email'] = row[6]
                    user['join_date'] = row[7]
                    user['deactivate_date'] = row[8]
                    user['license_number'] = row[9]
                    user['major'] = row[10]
                    user['certificate_dir'] = row[11]
            except Exception as e:
                print("Exception: ", e)
            finally:
                self.connector.close()
        return user

    def add_physician_profile(self, profile):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add patient profile to 'patient_profile' table
                physician_id = profile['physician_id']
                db_query = "INSERT INTO physician_profile (physician_id) VALUES (%s)"
                cursor.execute(db_query, (physician_id))
                self.connector.commit()
                row_id = cursor.lastrowid
                if row_id > 0:
                    if_inserted = True
            except Exception as e:
                print("Exception: ", e)
            finally:
                self.connector.close()
                return if_inserted

    def retrieve_physician_profile(self, physician_id, time_from=None):
        profiles = []
        date = int(time_from) if time_from is not None else 0
        db_query = "SELECT * FROM physician_profile WHERE physician_id=%s and timestamp>%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (physician_id, date))
                self.connector.commit()
                profile = {}
                for row in cursor:
                    profile['physician_profile_id'] = row[0]
                    profile['physician_id'] = row[1]
                    profile['timestamp'] = row[2]
                    profiles.append(profile)
            except Exception as e:
                print("Exception: ", e)
            finally:
                self.connector.close()
        return profiles

    def add_medical_image(self, medical_image):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add a medical image information to 'medical_image' table
                patient_id = medical_image['patient_id']
                subject = medical_image['subject']
                size = medical_image['size']
                type = medical_image['type']
                hospital = medical_image['hospital']
                asmt_date = medical_image['asmt_date']
                upload_date = medical_image['upload_date']
                exam_physician = medical_image['exam_physician']
                place = medical_image['place']
                description = medical_image['description']
                comment = medical_image['comment']
                db_query = "INSERT INTO medical_image (patient_id, subject, size, type, hospital, asmt_date, upload_date, exam_physician, place, description, comment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query, (patient_id, subject, size, type, hospital, asmt_date, upload_date, exam_physician, place, description, comment))
                self.connector.commit()
                row_id = cursor.lastrowid
                if row_id > 0:
                    if_inserted = True
            except Exception as e:
                print("Exception: ", e)
            finally:
                self.connector.close()
                return if_inserted

    def retrieve_medical_image(self, patient_id, time_from=None):
        images = []
        date = int(time_from) if time_from is not None else 0
        db_query = "SELECT * FROM medical_image WHERE patient_id=%s and asmt_date>%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (patient_id, date))
                self.connector.commit()
                image = {}
                for row in cursor:
                    image['image_id'] = row[0]
                    image['patient_id'] = row[1]
                    image['subject'] = row[2]
                    image['size'] = row[3]
                    image['type'] = row[4]
                    image['hospital'] = row[5]
                    image['asmt_date'] = row[6]
                    image['upload_date'] = row[7]
                    image['exam_physician'] = row[8]
                    image['place'] = row[9]
                    image['description'] = row[10]
                    image['comment'] = row[11]
                    images.append(image)
            except Exception as e:
                print("Exception: ", e)
            finally:
                self.connector.close()
        return images

    def add_interpretation(self, intpr):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add a interpretation result to 'interpretation' table
                physician_id = intpr['physician_id']
                image_id = intpr['image_id']
                level = intpr['level']
                fee = intpr['fee']
                date = intpr['date']
                summary = intpr['summary']
                status = intpr['status']
                db_query = "INSERT INTO interpretation (physician_id, image_id, level, fee, date, summary, status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query, (physician_id, image_id, level, fee, date, summary, status))
                self.connector.commit()
                row_id = cursor.lastrowid
                if row_id > 0:
                    if_inserted = True
            except Exception as e:
                print("Exception: ", e)
            finally:
                self.connector.close()
                return if_inserted

    def retrieve_intpr(self, image_id, time_from = None):
        intprs = []
        date = int(time_from) if time_from is not None else 0
        db_query = "SELECT * FROM interpretation WHERE image_id=%s and date>%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (image_id, date))
                self.connector.commit()
                intpr = {}
                for row in cursor:
                    intpr['intpr_id'] = row[0]
                    intpr['physician_id'] = row[1]
                    intpr['image_id'] = row[2]
                    intpr['level'] = row[3]
                    intpr['fee'] = row[4]
                    intpr['date'] = row[5]
                    intpr['summary'] = row[6]
                    intpr['status'] = row[7]
                    intprs.append(intpr)
            except Exception as e:
                print("Exception: ", e)
            finally:
                self.connector.close()
        return intprs

if __name__ == '__main__':
    db = DbManager()
    # patient = {
    #     'password': 1234,
    #     'user_type': 'Patient',
    #     'name': 'Ah Young Min',
    #     'gender': 'Female',
    #     'birth_date': 719427600000,
    #     'mobile': '01045586587',
    #     'email': 'min1018@gmail.com',
    #     'join_date': 1450371600000,
    #     'deactivate_date': 0
    # }
    # db.add_patient(patient)

    # physician = {
    #     'license_number': '23kljlfkaj9032k-234jl-lk23lk',
    #     'major': 'Heart',
    #     'certificate_dir': '/db/dd/djkel.jpg',
    #     'password': 1234,
    #     'user_type': 'Physician',
    #     'name': 'Ye Hwa Han',
    #     'gender': 'Female',
    #     'birth_date': 587926800000,
    #     'mobile': '01015765871',
    #     'email': 'han820@gmail.com',
    #     'join_date': 1450469913000,
    #     'deactivate_date': 0
    # }
    # db.add_physician(physician)

    # image = {
    #     'patient_id': 9,
    #     'subject': 'Heart',
    #     'size': 20,
    #     'type': 'ECG',
    #     'hospital': 'Seoul Hospital',
    #     'asmt_date': 1450469913000,
    #     'upload_date': 1480969913000,
    #     'exam_physician': 'Dr.Choi',
    #     'place': 'Seoul Hospital',
    #     'description': 'None',
    #     'comment': 'None'
    # }
    # db.add_medical_image(image)

    # intpr = {
    #     'physician_id': 3,
    #     'image_id': 1,
    #     'level': 1,
    #     'fee': 0,
    #     'date': 1450469913000,
    #     'summary': 'None',
    #     'status': 'None'
    # }
    # db.add_interpretation(intpr)

    # patient_profile = {
    #     'patient_id': 9,
    #     'height': 168,
    #     'weight': 62,
    #     'drink_capacity': 2,
    #     'drink_frequency': 1,
    #     'sleep_hour': 8,
    #     'exercise_hour': 4,
    #     'smoke_status': 'None',
    #     'water_intake': 8,
    #     'disease_history': 'None',
    #     'medication': 'None',
    #     'family_history': 'None',
    #     'significant': 'None',
    #     'notice': 'None'
    # }
    # db.add_patient_profile(patient_profile)

    # physician_profile = {
    #     'physician_id': 3
    # }
    # db.add_physician_profile(physician_profile)

    # patients = db.retrieve_patient(9)
    # print(patients)

    # physicians = db.retrieve_physician(3)
    # print(physicians)

    # intprs = db.retrieve_intpr(1)
    # print(intprs)

    # images = db.retrieve_medical_image(9)
    # print(images)

    # profiles = db.retrieve_patient_profile(9)
    # print(profiles)

    # profiles = db.retrieve_physician_profile(3)
    # print(profiles)