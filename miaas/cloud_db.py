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
                print("Retrieve_User: ", e)
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
                print("Find_User: ", e)
            finally:
                return if_exist

    def find_id(self, email, name):
        user_id = None
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT user_id FROM user WHERE email=%s AND name=%s"
                cursor.execute(db_query, (email, name))
                self.connector.commit()
                row = cursor.fetchone()
                user_id = row[0]
            except Exception as e:
                print("Find_ID: ", e)
        return user_id

    def find_passwd(self, user_id, email, name):
        passwd = None
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT password FROM user WHERE user_id=%s AND email=%s AND name=%s"
                cursor.execute(db_query, (user_id, email, name))
                self.connector.commit()
                row = cursor.fetchone()
                passwd = row[0]
            except Exception as e:
                print("Find_Passwd: ", e)
        return passwd

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
                print("Add_Patient: ", e)
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
                print("Retrieve_Patient: ", e)
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
            try:
                db_query = "UPDATE user as u INNER JOIN patient as p ON u.user_id=p.user_id SET u.password=%s, u.name=%s, u.phone_number=%s, u.email=%s, p.gender=%s, p.birthday=%s WHERE u.user_id=%s"
                cursor.execute(db_query, (password, name, phone_number, email, gender, birthday, user_id))
                self.connector.commit()
                row_count = cursor.rowcount
                print(row_count)
                if row_count > 0:
                    if_updated = True
            except Exception as e:
                print('Update_Patient: ', e)
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
                print("Add_Patient_Profile: ", e)
        return if_inserted

    # type='None' (performance low)
    def retrieve_patient_profile(self, patient_id, type=None):
        profiles = []
        if type is None:
            # Retrieve all profile types
            db_query = "SELECT type FROM patient_profile WHERE user_id=%s"
            with self.connector.cursor() as cursor:
                try:
                    cursor.execute(db_query, (patient_id))
                    self.connector.commit()
                    profile_types = []
                    for row in cursor:
                        profile_type = row[0]
                        if profile_type not in profile_types:
                            profile_types.append(profile_type)
                except Exception as e:
                    print("Retrieve_Patient_Profile on type list: ", e)
            # Retrieve patient profiles on 'type is not None'
            with self.connector.cursor() as cursor:
                db_query = "SELECT type, value, timestamp FROM patient_profile WHERE user_id=%s and type=%s ORDER BY timestamp DESC LIMIT 1"
                try:
                    for item in profile_types:
                        cursor.execute(db_query, (patient_id, item))
                        self.connector.commit()
                        row = cursor.fetchone()
                        profile = {}
                        profile['type'] = row[0]
                        profile['value'] = row[1]
                        profile['timestamp'] = row[2]
                        profiles.append(profile)
                except Exception as e:
                    print("Retrieve_Patient_Profile with type is None:", e)
        else:
            db_query = "SELECT type, value, timestamp FROM patient_profile WHERE user_id=%s and type=%s ORDER BY timestamp DESC"
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
                    print("Retrieve_Patient_Profile with type is not None: ", e)
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
                print("Add_Physician: ", e)
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
                print("Retrieve_Physician: ", e)
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
            try:
                db_query = "UPDATE user as u INNER JOIN physician as p ON u.user_id=p.user_id SET u.password=%s, u.name=%s, u.phone_number=%s, u.email=%s, p.license_number=%s, p.medicine_field=%s, p.certificate_dir=%s WHERE u.user_id=%s"
                cursor.execute(db_query, (
                password, name, phone_number, email, license_number, medicine_field, certificate_dir, user_id))
                self.connector.commit()
                row_count = cursor.rowcount
                print(row_count)
                if row_count > 0:
                    if_updated = True
            except Exception as e:
                print("Update_Physician:", e)
        return if_updated

    def add_physician_profile(self, user_id, type, value):
        if_exist = False
        # Check type existence
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT value FROM physician_profile WHERE user_id=%s AND type=%s"
                cursor.execute(db_query, (user_id, type))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_exist = True
                if if_exist:
                    # Update current physician profile
                    if_updated = False
                    db_query = "UPDATE physician_profile SET value=%s WHERE user_id=%s AND type=%s"
                    cursor.execute(db_query, (value, user_id, type))
                    self.connector.commit()
                    row_count = cursor.rowcount
                    if row_count > 0:
                        if_updated = True
                    return if_updated
                else:
                    # Add physician profile to 'physician_profile' table
                    if_inserted = False
                    db_query = "INSERT INTO physician_profile (user_id, type, value) VALUES (%s, %s, %s)"
                    cursor.execute(db_query, (user_id, type, value))
                    self.connector.commit()
                    row_count = cursor.rowcount
                    if row_count > 0:
                        if_inserted = True
                    return if_inserted
            except Exception as e:
                print("Add_Physician_Profile: ", e)

    def retrieve_physician_profile(self, physician_id, type=None):
        profiles = []
        with self.connector.cursor() as cursor:
            try:
                if type is None:
                    db_query = "SELECT type, value FROM physician_profile WHERE user_id=%s"
                    cursor.execute(db_query, physician_id)
                else:
                    db_query = "SELECT type, value FROM physician_profile WHERE user_id=%s and type=%s"
                    cursor.execute(db_query, physician_id, type)
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
                user_id = medical_image['user_id']
                subject = medical_image['subject']
                image_type = medical_image['image_type']
                taken_from = medical_image['taken_from']
                physician = medical_image['physician']
                place = medical_image['place']
                description = medical_image['description']
                # image_dir = medical_image['image_dir']
                image_dir = 'DUMMY_DIR'
                # size = medical_image['size']
                timestamp = medical_image['timestamp']
                db_query = "INSERT INTO medical_image (user_id, subject, image_type, taken_from, physician, place, description, image_dir, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query, (
                user_id, subject, image_type, taken_from, physician, place, description, image_dir, timestamp))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
            except Exception as e:
                print("Add_Medical_Image: ", e)
            finally:
                return if_inserted

    # To update a medical image information by 'image_id'
    def update_medical_image_by_id(self, medical_image):
        if_updated = False
        image_id = medical_image['image_id']
        subject = medical_image['subject']
        image_type = medical_image['image_type']
        taken_from = medical_image['taken_from']
        physician = medical_image['physician']
        place = medical_image['place']
        description = medical_image['description']
        timestamp = medical_image['timestamp']
        with self.connector.cursor() as cursor:
            try:
                db_query = "UPDATE medical_image SET subject=%s, image_type=%s, taken_from=%s, physician=%s, place=%s, description=%s, timestamp=%s WHERE image_id=%s"
                cursor.execute(db_query, (subject, image_type, taken_from, physician, place, description, timestamp, image_id))
                self.connector.commit()
                row_count = cursor.rowcount
                print(row_count)
                if row_count > 0:
                    if_updated = True
            except Exception as e:
                print("Update_Medical_Image:", e)
        return if_updated

    def retrieve_medical_image(self, user_id, time_from=None, offset=None, limit=None):
        images = []
        time_from = int(time_from) if time_from is not None else 0
        offset = int(offset) if offset is not None else 0
        limit = int(limit) if limit is not None else 0
        with self.connector.cursor() as cursor:
            try:
                if limit is 0:
                    db_query = "SELECT * FROM medical_image WHERE user_id=%s and timestamp>=%s ORDER BY timestamp DESC"
                    cursor.execute(db_query, (user_id, time_from))
                else:
                    db_query = "SELECT * FROM medical_image WHERE user_id=%s and timestamp>=%s ORDER BY timestamp DESC LIMIT %s OFFSET %s"
                    cursor.execute(db_query, (user_id, time_from, limit, offset))
                self.connector.commit()
                for row in cursor:
                    image = {}
                    image['image_id'] = row[0]
                    image['user_id'] = row[1]
                    image['subject'] = row[2]
                    image['image_type'] = row[3]
                    image['taken_from'] = row[4]
                    image['physician'] = row[5]
                    image['place'] = row[6]
                    image['description'] = row[7]
                    image['image_dir'] = row[8]
                    image['size'] = row[9]
                    image['timestamp'] = row[10]
                    image['intpr_num'] = row[11]
                    images.append(image)
            except Exception as e:
                print("Retrieve_Medical_Image: ", e)
        return images

    def retrieve_medical_image_amount(self, patient_id):
        amount = -1
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT * FROM medical_image WHERE user_id=%s"
                cursor.execute(db_query, (patient_id))
                self.connector.commit()
                amount = cursor.rowcount
            except Exception as e:
                print("Retrieve_Medical_Image_Amount: ", e)
        return amount

    def retrieve_medical_image_by_id(self, image_id):
        db_query = "SELECT * FROM medical_image WHERE image_id=%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (image_id))
                self.connector.commit()
                row = cursor.fetchone()
                image = {}
                image['image_id'] = row[0]
                image['user_id'] = row[1]
                image['subject'] = row[2]
                image['image_type'] = row[3]
                image['taken_from'] = row[4]
                image['physician'] = row[5]
                image['place'] = row[6]
                image['description'] = row[7]
                image['image_dir'] = row[8]
                image['size'] = row[9]
                image['timestamp'] = row[10]
                image['intpr_num'] = row[11]
            except Exception as e:
                print("Retrieve_Medical_Image_By_Id: ", e)
        return image

    def add_intpr(self, intpr):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add a interpretation result to 'interpretation' table
                patient_id = intpr['patient_id']
                image_id = intpr['image_id']
                level = intpr['level']
                fee = intpr['fee']
                timestamp = intpr['timestamp']
                summary = intpr['summary']
                interpretation = intpr['interpretation']
                status = intpr['status']
                subject = intpr['subject']
                message = intpr['message']
                request_id = intpr['request_id']
                db_query = "INSERT INTO interpretation (patient_id, image_id, level, fee, timestamp, summary, interpretation, status, subject, message, request_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query, (patient_id, image_id, level, fee, timestamp, summary, interpretation, status, subject, message, request_id))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
            except Exception as e:
                print("Add_Interpretation: ", e)
            finally:
                return if_inserted

    def retrieve_intpr_by_id(self, intpr_id):
        db_query = "SELECT * FROM interpretation WHERE intpr_id=%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (intpr_id))
                self.connector.commit()
                row = cursor.fetchone()
                intpr = {}
                intpr['intpr_id'] = row[0]
                intpr['physician_id'] = row[1]
                intpr['patient_id'] = row[2]
                intpr['image_id'] = row[3]
                intpr['level'] = row[4]
                intpr['fee'] = row[5]
                intpr['timestamp'] = row[6]
                intpr['summary'] = row[7]
                intpr['interpretation'] = row[8]
            except Exception as e:
                print("Retrieve_Interpretation_By_Id: ", e)
        return intpr

    # To retrieve all interpretation information from 'interpretation' table on 'image_id' arguments with medical image information from 'medical_image'
    def retrieve_image_and_intpr(self, image_id):
        intpr_by_image = {}
        intpr_list = []
        with self.connector.cursor() as cursor:
            try:
                # To retrieve data from 'medical_image' table
                db_query = "SELECT * FROM medical_image WHERE image_id=%s"
                cursor.execute(db_query, (image_id))
                self.connector.commit()
                row = cursor.fetchone()
                image = {}
                image['image_id'] = image_id
                image['user_id'] = row[1]
                image['subject'] = row[2]
                image['image_type'] = row[3]
                image['taken_from'] = row[4]
                image['physician'] = row[5]
                image['place'] = row[6]
                image['description'] = row[7]
                image['image_dir'] = row[8]
                image['size'] = row[9]
                image['timestamp'] = row[10]
                image['intpr_num'] = row[11]
                intpr_by_image['image'] = image
                # To retrieve data from 'interpretation' table
                db_query = "SELECT * FROM interpretation WHERE image_id=%s"
                cursor.execute(db_query, (image_id))
                self.connector.commit()
                for row in cursor:
                    intpr = {}
                    intpr['intpr_id'] = row[0]
                    intpr['patient_id'] = row[1]
                    intpr['level'] = row[3]
                    intpr['fee'] = row[4]
                    intpr['timestamp'] = row[5]
                    intpr['summary'] = row[6]
                    intpr['interpretation'] = row[7]
                    intpr['status'] = row[8]
                    intpr['subject'] = row[9]
                    intpr['message'] = row[10]
                    intpr_list.append(intpr)
                intpr_by_image['intpr'] = intpr_list
            except Exception as e:
                print("Retrieve_Interpretation_by_Image: ", e)
        return intpr_by_image

    def retrieve_image_intpr(self, image_id, time_from=None, offset=None, limit=None):
        intprs = []
        time_from = int(time_from) if time_from is not None else 0
        offset = int(offset) if offset is not None else 0
        limit = int(limit) if limit is not None else 0
        with self.connector.cursor() as cursor:
            if limit is 0:
                db_query = "SELECT * FROM interpretation WHERE image_id=%s and timestamp>%s ORDER BY timestamp DESC"
                cursor.execute(db_query, (image_id, time_from))
            else:
                db_query = "SELECT * FROM interpretation WHERE image_id=%s and timestamp>%s ORDER BY timestamp DESC LIMIT %s OFFSET %s"
                cursor.execute(db_query, (image_id, time_from, limit, offset))
            try:
                self.connector.commit()
                for row in cursor:
                    intpr = {}
                    intpr['intpr_id'] = row[0]
                    intpr['physician_id'] = row[1]
                    intpr['patient_id'] = row[2]
                    intpr['image_id'] = row[3]
                    intpr['level'] = row[4]
                    intpr['fee'] = row[5]
                    intpr['timestamp'] = row[6]
                    intpr['summary'] = row[7]
                    intpr['interpretation'] = row[8]
                    intprs.append(intpr)
            except Exception as e:
                print("Retrieve_Interpretation: ", e)
        return intprs

    # KH
    def retrieve_physician_intpr_list(self, physician_id, time_from=None):
        intprs = []
        time_from = int(time_from) if time_from is not None else 0
        db_query = "SELECT intpr_id, physician_id, patient_id, interpretation.image_id, level, fee, interpretation.timestamp, summary, status, interpretation.subject as request_subject, message, medical_image.subject as image_subject, image_type, taken_from " \
                   "FROM miaas.interpretation join miaas.medical_image " \
                   "WHERE interpretation.image_id = medical_image.image_id and interpretation.physician_id=%s and interpretation.timestamp>%s " \
                   "ORDER BY interpretation.timestamp DESC"

        print(db_query%(physician_id, time_from))
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (physician_id, time_from))
                self.connector.commit()
                for row in cursor:
                    intpr = {}
                    intpr['intpr_id'] = row[0]
                    intpr['physician_id'] = row[1]
                    intpr['patient_id'] = row[2]
                    intpr['image_id'] = row[3]
                    intpr['level'] = row[4]
                    intpr['fee'] = row[5]
                    intpr['timestamp'] = row[6]
                    intpr['summary'] = row[7]
                    intpr['status'] = row[8]
                    intpr['request_subject'] = row[8]
                    intpr['message'] = row[9]
                    intpr['image_subject'] = row[10]
                    intpr['image_type'] = row[11]
                    intpr['taken_from'] = row[12]
                    intprs.append(intpr)
            except Exception as e:
                print("Retrieve_Physician_Interpretation: ", e)
        return intprs

    def retrieve_physician_intpr(self, physician_id, time_from=None):
        intprs = []
        time_from = int(time_from) if time_from is not None else 0
        db_query = "SELECT * FROM interpretation WHERE physician_id=%s and timestamp>%s ORDER BY timestamp DESC"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (physician_id, time_from))
                self.connector.commit()
                for row in cursor:
                    intpr = {}
                    intpr['intpr_id'] = row[0]
                    intpr['physician_id'] = row[1]
                    intpr['patient_id'] = row[2]
                    intpr['image_id'] = row[3]
                    intpr['level'] = row[4]
                    intpr['fee'] = row[5]
                    intpr['timestamp'] = row[6]
                    intpr['summary'] = row[7]
                    intpr['interpretation'] = row[8]
                    intprs.append(intpr)
            except Exception as e:
                print("Retrieve_Physician_Interpretation: ", e)
        return intprs

    def retrieve_physician_intpr_amount(self, physician_id):
        amount = -1
        db_query = "SELECT * FROM interpretation WHERE physician_id=%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (physician_id))
                self.connector.commit()
                amount = cursor.rowcount
            except Exception as e:
                print("Retrieve_Physician_Interpretation_Amount: ", e)
        return amount

    def add_analytic(self, analytic):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add a analytic result to 'analytic' table
                image_id = analytic['image_id']
                level = analytic['level']
                fee = analytic['fee']
                timestamp = analytic['timestamp']
                summary = analytic['summary']
                result = analytic['result']
                db_query = "INSERT INTO analytic (image_id, level, fee, timestamp, summary, result) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query, (image_id, level, fee, timestamp, summary, result))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
            except Exception as e:
                print("Add_Analytics: ", e)
        return if_inserted

    def retrieve_analytic_by_image(self, image_id):
        analtics = []
        db_query = "SELECT * FROM analytic WHERE image_id=%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (image_id))
                self.connector.commit()
                for row in cursor:
                    anal = {}
                    anal['intpr_id'] = row[0]
                    anal['image_id'] = row[1]
                    anal['level'] = row[2]
                    anal['fee'] = row[3]
                    anal['timestamp'] = row[4]
                    anal['summary'] = row[5]
                    anal['result'] = row[6]
                    analtics.append(anal)
            except Exception as e:
                print("Retrieve_Interpretation_By_Id: ", e)
        return analtics

    def update_analytic(self, level, fee, timestamp, summary, result, anal_id):
        if_updated = False
        with self.connector.cursor() as cursor:
            try:
                db_query = "UPDATE analytic SET level=%s, fee=%s, timestamp=%s, summary=%s, result=%s WHERE anal_id=%s"
                cursor.execute(db_query, (level, fee, timestamp, summary, result, anal_id))
                self.connector.commit()
                row_count = cursor.rowcount
                print(row_count)
                if row_count > 0:
                    if_updated = True
            except Exception as e:
                print("Update_Analytic:", e)
        return if_updated

    # KH
    def retrieve_patient_request_list(self, patient_id, time_from=None):
        requests = []
        time_from = int(time_from) if time_from is not None else 0
        db_query = "SELECT * " \
                   "FROM miaas.request join miaas.medical_image " \
                   "WHERE request.image_id = medical_image.image_id and medical_image.user_id=%s and request.timestamp>%s " \
                   "ORDER BY request.timestamp DESC"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (patient_id, time_from))
                self.connector.commit()
                for row in cursor:
                    request = {}
                    request['request_id'] = row[0]
                    request['image_id'] = row[1]
                    request['status'] = row[2]
                    request['request_subject'] = row[3]
                    request['message'] = row[4]
                    request['request_date'] = row[5]
                    request['level'] = row[6]
                    request['patient_id'] = row[8]
                    request['image_subject'] = row[8]
                    request['image_type'] = row[9]
                    request['taken_from'] = row[10]
                    request['upload_date'] = row[17]
                    requests.append(request)
            except Exception as e:
                print("Retrieve_Physician_Interpretation: ", e)
        return requests

    #
    def retrieve_requested_intpr_amount(self, query_type=None, image_subject=None, image_type=None, time_from=None):
        amount = -1
        time_from = int(time_from) if time_from is not None else 0
        if query_type == "Image Type" and image_type is not None:
            db_query = "SELECT * " \
                       "FROM miaas.interpretation join miaas.medical_image " \
                       "WHERE interpretation.image_id = medical_image.image_id and status <= 1 and image_type='%s' and interpretation.timestamp>%s " \
                       "ORDER BY status DESC"%(image_type, time_from)

        elif query_type == "Request Subject" and image_subject is not None:
            db_query = "SELECT * " \
                       "FROM miaas.interpretation join miaas.medical_image " \
                       "WHERE interpretation.image_id = medical_image.image_id and status <= 1 and subject Like '%s' and  interpretation.timestamp>%s " \
                       "ORDER BY status DESC"%("%" + image_subject + "%", time_from)

        else:
            db_query = "SELECT * " \
                       "FROM miaas.interpretation join miaas.medical_image " \
                       "WHERE interpretation.image_id = medical_image.image_id and status <= 1 and interpretation.timestamp>%s " \
                       "ORDER BY status DESC"%time_from

        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query)
                self.connector.commit()
                amount = cursor.rowcount
            except Exception as e:

                print("Retrieve_Requested_Interpretation_Amount: ", e)
        return amount

    # KH
    def retrieve_patient_intpr_list(self, patient_id, time_from=None):
        intprs = []
        time_from = int(time_from) if time_from is not None else 0
        db_query = "SELECT * " \
                   "FROM miaas.request join miaas.medical_image " \
                   "WHERE request.image_id = medical_image.image_id and medical_image.user_id=%s and request.timestamp>%s " \
                   "ORDER BY request.timestamp DESC"

        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (patient_id, time_from))
                self.connector.commit()
                for row in cursor:
                    intpr = {}
                    intpr['intpr_id'] = row[0]
                    intpr['physician_id'] = row[1]
                    intpr['patient_id'] = row[2]
                    intpr['image_id'] = row[3]
                    intpr['level'] = row[4]
                    intpr['fee'] = row[5]
                    intpr['timestamp'] = row[6]
                    intpr['summary'] = row[7]
                    intpr['status'] = row[8]
                    intpr['request_subject'] = row[8]
                    intpr['message'] = row[9]
                    intpr['image_subject'] = row[10]
                    intpr['image_type'] = row[11]
                    intpr['taken_from'] = row[12]
                    intprs.append(intpr)
            except Exception as e:
                print("Retrieve_Physician_Interpretation: ", e)
        return intprs

    # KH
    def retrieve_requested_intpr_list(self, query_type=None, image_subject=None, image_type=None, time_from=None):
        intprs = []
        time_from = int(time_from) if time_from is not None else 0
        if query_type == "Image Type" and image_type is not None:
            db_query = "SELECT intpr_id, physician_id, patient_id, interpretation.image_id, level, fee, interpretation.timestamp, summary, status, interpretation.subject as request_subject, message, medical_image.subject as image_subject, image_type, taken_from " \
                       "FROM miaas.interpretation join miaas.medical_image " \
                       "WHERE interpretation.image_id = medical_image.image_id and status >= 2 and image_type='%s' and interpretation.timestamp>%s " \
                       "ORDER BY status DESC"%(image_type, time_from)

        elif query_type == "Request Subject" and image_subject is not None:
            db_query = "SELECT intpr_id, physician_id, patient_id, interpretation.image_id, level, fee, interpretation.timestamp, summary, status, interpretation.subject as request_subject, message, medical_image.subject as image_subject, image_type, taken_from " \
                       "FROM miaas.interpretation join miaas.medical_image " \
                       "WHERE interpretation.image_id = medical_image.image_id and status >= 2 and subject Like '%s' and  interpretation.timestamp>%s " \
                       "ORDER BY status DESC"%("%" + image_subject + "%", time_from)

        else:
            db_query = "SELECT intpr_id, physician_id, patient_id, interpretation.image_id, level, fee, interpretation.timestamp, summary, status, interpretation.subject as request_subject, message, medical_image.subject as image_subject, image_type, taken_from " \
                       "FROM miaas.interpretation join miaas.medical_image " \
                       "WHERE interpretation.image_id = medical_image.image_id and status >= 2 and interpretation.timestamp>%s " \
                       "ORDER BY status DESC"%time_from

        print(db_query)
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query)
                self.connector.commit()
                for row in cursor:
                    intpr = {}
                    intpr['intpr_id'] = row[0]
                    intpr['physician_id'] = row[1]
                    intpr['patient_id'] = row[2]
                    intpr['image_id'] = row[3]
                    intpr['level'] = row[4]
                    intpr['fee'] = row[5]
                    intpr['timestamp'] = row[6]
                    intpr['summary'] = row[7]
                    intpr['status'] = row[8]
                    intpr['request_subject'] = row[8]
                    intpr['message'] = row[9]
                    intpr['image_subject'] = row[10]
                    intpr['image_type'] = row[11]
                    intpr['taken_from'] = row[12]
                    intprs.append(intpr)
            except Exception as e:
                print("Retrieve_Physician_Interpretation: ", e)
        return intprs

    # KH
    def retrieve_requested_intpr_amount(self, query_type=None, image_subject=None, image_type=None, time_from=None):
        amount = -1
        time_from = int(time_from) if time_from is not None else 0
        if query_type == "Image Type" and image_type is not None:
            db_query = "SELECT * " \
                       "FROM miaas.interpretation join miaas.medical_image " \
                       "WHERE interpretation.image_id = medical_image.image_id and status <= 1 and image_type='%s' and interpretation.timestamp>%s " \
                       "ORDER BY status DESC"%(image_type, time_from)

        elif query_type == "Request Subject" and image_subject is not None:
            db_query = "SELECT * " \
                       "FROM miaas.interpretation join miaas.medical_image " \
                       "WHERE interpretation.image_id = medical_image.image_id and status <= 1 and subject Like '%s' and  interpretation.timestamp>%s " \
                       "ORDER BY status DESC"%("%" + image_subject + "%", time_from)

        else:
            db_query = "SELECT * " \
                       "FROM miaas.interpretation join miaas.medical_image " \
                       "WHERE interpretation.image_id = medical_image.image_id and status <= 1 and interpretation.timestamp>%s " \
                       "ORDER BY status DESC"%time_from

        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query)
                self.connector.commit()
                amount = cursor.rowcount
            except Exception as e:

                print("Retrieve_Requested_Interpretation_Amount: ", e)
        return amount

    def retrieve_patient_intpr(self, patient_id, time_from=None):
        intprs = []
        time_from = int(time_from) if time_from is not None else 0
        db_query = "SELECT * FROM interpretation WHERE patient_id=%s and timestamp>%s ORDER BY timestamp DESC"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (patient_id, time_from))
                self.connector.commit()
                for row in cursor:
                    intpr = {}
                    intpr['intpr_id'] = row[0]
                    intpr['physician_id'] = row[1]
                    intpr['patient_id'] = row[2]
                    intpr['image_id'] = row[3]
                    intpr['level'] = row[4]
                    intpr['fee'] = row[5]
                    intpr['timestamp'] = row[6]
                    intpr['summary'] = row[7]
                    intpr['interpretation'] = row[8]
                    intprs.append(intpr)
            except Exception as e:
                print("Retrieve_Physician_Interpretation: ", e)
        return intprs

    def retrieve_patient_intpr_amount(self, patient_id):
        amount = -1
        db_query = "SELECT * FROM interpretation WHERE patient_id=%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (patient_id))
                self.connector.commit()
                amount = cursor.rowcount
            except Exception as e:
                print("Retrieve_Patient_Interpretation_Amount: ", e)
        return amount

    def add_patient_intpr_request(self, request):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add request information to 'request' table
                image_id = request['image_id']
                status = request['status']
                subject = request['subject']
                message = request['message']
                timestamp = request['timestamp']
                db_query = "INSERT INTO request (image_id, status, subject, message, timestamp) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(db_query, (image_id, status, subject, message, timestamp))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
            except Exception as e:
                print("Add_Patient_Intpr_Request: ", e)
        return if_inserted

    def update_patient_request_by_selection(self, request_id, physician_id, status, timestamp):
        if_updated = False
        with self.connector.cursor() as cursor:
            try:
                db_query = "UPDATE request SET status=%s, timestamp=%s WHERE request_id=%s"
                cursor.execute(db_query, (status, timestamp, request_id))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    db_query = "DELETE from response WHERE request_id=%s AND physician_id!=%s"
                    cursor.execute(db_query, (request_id, physician_id))
                    self.connector.commit()
                    row_count = cursor.rowcount
                    if row_count > 0:
                        if_updated = True
            except Exception as e:
                print("Update_Patient_Request_by_Selection:", e)
        return if_updated

    def add_physician_intpr_resp(self, response):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add response information to 'response' table
                request_id = response['request_id']
                physician_id = response['physician_id']
                message = response['message']
                timestamp = response['timestamp']
                db_query = "INSERT INTO response (request_id, physician_id, message, timestamp) VALUES (%s, %s, %s, %s)"
                cursor.execute(db_query, (request_id, physician_id, message, timestamp))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
            except Exception as e:
                print("Add_Physician_Intpr_Response: ", e)
        return if_inserted