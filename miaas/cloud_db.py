__author__ = 'Jincheul'


import pymysql
import logging

logging.basicConfig(
    format="[%(name)s][%(asctime)s] %(message)s",
    handlers=[logging.StreamHandler()],
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DbManager():
    def __init__(self):
        host = 'rainbowdb.czg2t6iatylv.us-west-2.rds.amazonaws.com'
        user = 'smartylab'
        port = 3306
        password = 'lovejesus'
        dbName = 'miaas'
        try:
            self.connector = pymysql.connect(host=host, port=port, user=user, passwd=password, db=dbName)
            self.is_connected = True
        except Exception as e:
            print(e)
            self.is_connected = False

    def retrieve_user(self, user_id, password):
        user_type = None
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT user_type FROM user WHERE user_id=%s and password=%s"
                cursor.execute(db_query, (user_id, password))
                self.connector.commit()
                row = cursor.fetchone()
                user_type = row[0]
            except Exception as e:
                print("Exception: ", e)
            finally:
                return user_type

    def find_user(self, user_id):
        if_exist = False
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT * FROM user WHERE user_id=%s"
                cursor.execute(db_query, (user_id))
                self.connector.commit()
                row = cursor.fetchone()
                if row is not None:
                    if_exist = True
            except Exception as e:
                print("Exception: ", e)
            finally:
                return if_exist

    def add_patient(self, patient):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add patient information to 'user' table
                user_id = patient['user_id']
                password = patient['password']
                name = patient['name']
                phone_number = patient['phone_number']
                email = patient['email']
                join_date = patient['join_date']
                user_type = patient['user_type']
                db_query = "INSERT INTO user (user_id, password, name, phone_number, email, join_date, user_type) values (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query, (user_id, password, name, phone_number, email, join_date, user_type))
                self.connector.commit()
                # Add patient information to 'user' table
                gender = patient['gender']
                birthday = patient['birthday']
                db_query = "INSERT INTO patient (user_id, gender, birthday) VALUES (%s, %s, %s)"
                cursor.execute(db_query, (user_id, gender, birthday))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
            except Exception as e:
                print("Exception: ", e)
            finally:
                return if_inserted

    def retrieve_patient(self, patient_id, password=None):
        user = {}
        with self.connector.cursor() as cursor:
            try:
                if password is None:
                    db_query = "SELECT u.name, u.phone_number, u.email, u.join_date, u.deactivate_date, u.user_type, p.gender, p.birthday FROM patient as p LEFT JOIN user as u on p.user_id=u.user_id WHERE u.user_id=%s"
                    cursor.execute(db_query, (patient_id))
                else:
                    db_query = "SELECT u.name, u.phone_number, u.email, u.join_date, u.deactivate_date, u.user_type, p.gender, p.birthday, u.password FROM patient as p LEFT JOIN user as u on p.user_id=u.user_id WHERE u.user_id=%s and u.password=%s"
                    cursor.execute(db_query, (patient_id, password))
                self.connector.commit()
                for row in cursor:
                    user['user_id'] = patient_id
                    user['name'] = row[0]
                    user['phone_number'] = row[1]
                    user['email'] = row[2]
                    user['join_date'] = row[3]
                    user['deactivate_date'] = row[4]
                    user['user_type'] = row[5]
                    user['gender'] = row[6]
                    user['birthday'] = row[7]
                    if password is None:
                        user['password'] = None
                    else:
                        user['password'] = row[8]
            except Exception as e:
                print("Exception: ", e)
        return user

    def update_patient(self, user):
        if_updated = False
        user_id = user['user_id']
        password = user['password']
        name = user['name']
        phone_number = user['phone_number']
        email = user['email']
        gender = user['gender']
        birthday = user['birthday']
        with self.connector.cursor() as cursor:
            db_query = "UPDATE user as u INNER JOIN patient as p ON u.user_id=p.user_id SET u.password=%s, u.name=%s, u.phone_number=%s, u.email=%s, p.gender=%s, p.birthday=%s WHERE u.user_id=%s"
            cursor.execute(db_query, (password, name, phone_number, email, gender, birthday, user_id))
            self.connector.commit()
            row_count=cursor.rowcount
            print(row_count)
            if row_count > 0:
                if_updated = True
        return if_updated

    def add_patient_profile(self, user_id, type, value, timestamp):
        logger.info('user_id=%s type=%s value=%s' % (user_id, type, value))

        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add patient profile to 'patient_profile' table
                db_query = "INSERT INTO patient_profile (user_id, type, value, timestamp) VALUES (%s, %s, %s, %s)"
                cursor.execute(db_query, (user_id, type, value, timestamp))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
            except Exception as e:
                print("Exception: ", e)
            finally:
                return if_inserted

    def retrieve_patient_profile(self, patient_id, type=None):
        profiles = []
        if type is None:
            db_query = "SELECT type, value, timestamp FROM patient_profile WHERE user_id=%s"
        else:
            db_query = "SELECT type, value, timestamp FROM patient_profile WHERE user_id=%s and type=%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (patient_id, type))
                self.connector.commit()
                for row in cursor:
                    profile = {}
                    profile['type'] = row[0]
                    profile['value'] = row[1]
                    profile['timestamp'] = row[2]
                    profiles.append(profile)
            except Exception as e:
                print("Exception: ", e)
        return profiles

    def add_physician(self, physician):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add physician information to 'user' table
                user_id = physician['user_id']
                password = physician['password']
                name = physician['name']
                phone_number = physician['phone_number']
                email = physician['email']
                join_date = physician['join_date']
                user_type = physician['user_type']
                db_query = "INSERT INTO user (user_id, password, name, phone_number, email, join_date, user_type) values (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query, (user_id, password, name, phone_number, email, join_date, user_type))
                self.connector.commit()
                # Add physician information to 'physician' table
                license_number = physician['license_number']
                medicine_field = physician['major']
                certificate_dir = physician['certificate_dir']
                db_query = "INSERT INTO physician (user_id, license_number, medicine_field, certificate_dir) values (%s, %s, %s, %s)"
                cursor.execute(db_query, (user_id, license_number, medicine_field, certificate_dir))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
            except Exception as e:
                print("Exception: ", e)
            finally:
                return if_inserted

    def retrieve_physician(self, physician_id, password=None):
        user = {}
        with self.connector.cursor() as cursor:
            try:
                if password is None:
                    db_query = "SELECT u.name, u.phone_number, u.email, u.join_date, u.deactivate_date, u.user_type, p.license_number, p.medicine_field, p.certificate_dir FROM physician as p LEFT JOIN user as u on p.user_id=u.user_id WHERE u.user_id=%s"
                    cursor.execute(db_query, (physician_id))
                else:
                    db_query = "SELECT u.name, u.phone_number, u.email, u.join_date, u.deactivate_date, u.user_type, p.license_number, p.medicine_field, p.certificate_dir, u.password FROM physician as p LEFT JOIN user as u on p.user_id=u.user_id WHERE u.user_id=%s and u.password=%s"
                    cursor.execute(db_query, (physician_id, password))
                self.connector.commit()
                for row in cursor:
                    user['user_id'] = physician_id
                    user['name'] = row[0]
                    user['phone_number'] = row[1]
                    user['email'] = row[2]
                    user['join_date'] = row[3]
                    user['deactivate_date'] = row[4]
                    user['user_type'] = row[5]
                    user['license_number'] = row[6]
                    user['medicine_field'] = row[7]
                    user['certificate_dir'] = row[8]
                    if password is None:
                        user['password'] = None
                    else:
                        user['password'] = row[9]
            except Exception as e:
                print("Exception: ", e)
        return user

    def update_physician(self, user):
        if_updated = False
        user_id = user['user_id']
        password = user['password']
        name = user['name']
        phone_number = user['phone_number']
        email = user['email']
        license_number = user['license_number']
        medicine_field = user['medicine_field']
        certificate_dir = user['certificate_dir']
        with self.connector.cursor() as cursor:
            db_query = "UPDATE user as u INNER JOIN physician as p ON u.user_id=p.user_id SET u.password=%s, u.name=%s, u.phone_number=%s, u.email=%s, p.license_number=%s, p.medicine_field=%s, p.certificate_dir=%s WHERE u.user_id=%s"
            cursor.execute(db_query, (password, name, phone_number, email, license_number, medicine_field, certificate_dir, user_id))
            self.connector.commit()
            row_count=cursor.rowcount
            print(row_count)
            if row_count > 0:
                if_updated = True
        return if_updated

    def add_physician_profile(self, user_id, type, value):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add physician profile to 'physician_profile' table
                db_query = "INSERT INTO physician_profile (user_id, type, value) VALUES (%s, %s, %s)"
                cursor.execute(db_query, (user_id, type, value))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
            except Exception as e:
                print("Exception: ", e)
            finally:
                return if_inserted

    def retrieve_physician_profile(self, physician_id):
        profiles = []
        db_query = "SELECT type, value FROM physician_profile WHERE user_id=%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, physician_id)
                self.connector.commit()
                for row in cursor:
                    profile = {}
                    profile['type'] = row[0]
                    profile['value'] = row[1]
                    profiles.append(profile)
            except Exception as e:
                print("Exception: ", e)
        return profiles

    def add_medical_image(self, medical_image):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add a medical image information to 'medical_image' table
                subject = medical_image['subject']
                image_type = medical_image['image_type']
                taken_from = medical_image['taken_from']
                physician = medical_image['physician']
                place = medical_image['place']
                description = medical_image['description']
                comment = medical_image['comment']
                image_dir = medical_image['image_dir']
                user_id = medical_image['user_id']
                size = medical_image['size']
                db_query = "INSERT INTO medical_image (subject, image_type, taken_from, physician, place, description, comment, image_dir, user_id, size) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query, (subject, image_type, taken_from, physician, place, description, comment, image_dir, user_id, size))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
            except Exception as e:
                print("Exception: ", e)
            finally:
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
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
            except Exception as e:
                print("Exception: ", e)
            finally:
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
        return intprs