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
                cursor.execute(db_query,
                               (subject, image_type, taken_from, physician, place, description, timestamp, image_id))
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
                physician_id = intpr['physician_id']
                image_id = intpr['image_id']
                level = intpr['level']
                fee = intpr['fee']
                timestamp = intpr['timestamp']
                summary = intpr['summary']
                interpretation = intpr['interpretation']
                request_id = intpr['request_id']
                db_query = "INSERT INTO interpretation (patient_id, physician_id, image_id, level, fee, timestamp, summary, interpretation, request_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query, (patient_id, physician_id, image_id, level, fee, timestamp, summary, interpretation, request_id))
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
                intpr['patient_id'] = row[1]
                intpr['physician_id'] = row[2]
                intpr['image_id'] = row[3]
                intpr['level'] = row[4]
                intpr['fee'] = row[5]
                intpr['timestamp'] = row[6]
                intpr['summary'] = row[7]
                intpr['interpretation'] = row[8]
                intpr['request_id'] = row[9]
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
                    intpr['physician_id'] = row[2]
                    intpr['level'] = row[4]
                    intpr['fee'] = row[5]
                    intpr['timestamp'] = row[6]
                    intpr['summary'] = row[7]
                    intpr['interpretation'] = row[8]
                    intpr['request_id'] = row[9]
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
                    intpr['request_id'] = row[9]
                    intprs.append(intpr)
            except Exception as e:
                print("Retrieve_Interpretation: ", e)
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
                    intpr['patient_id'] = row[1]
                    intpr['physician_id'] = row[2]
                    intpr['image_id'] = row[3]
                    intpr['level'] = row[4]
                    intpr['fee'] = row[5]
                    intpr['timestamp'] = row[6]
                    intpr['summary'] = row[7]
                    intpr['interpretation'] = row[8]
                    intpr['request_id'] = row[9]
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
                    intpr['patient_id'] = row[1]
                    intpr['physician_id'] = row[2]
                    intpr['image_id'] = row[3]
                    intpr['level'] = row[4]
                    intpr['fee'] = row[5]
                    intpr['timestamp'] = row[6]
                    intpr['summary'] = row[7]
                    intpr['interpretation'] = row[8]
                    intpr['request_id'] = row[9]
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
                level = request['level']
                db_query = "INSERT INTO request (image_id, status, subject, message, timestamp, level) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query, (image_id, status, subject, message, timestamp, level))
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
                    if row_count > -1:
                        if_updated = True
            except Exception as e:
                print("Update_Patient_Request_by_Selection:", e)
        return if_updated

    def update_patient_request(self, request_id, subject, message, timestamp):
        if_updated = False
        with self.connector.cursor() as cursor:
            try:
                db_query = "UPDATE request SET subject=%s, message=%s, timestamp=%s WHERE request_id=%s"
                cursor.execute(db_query, (subject, message, timestamp, request_id))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_updated = True
            except Exception as e:
                print("Update_Patient_Request:", e)
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
                status = response['status']
                db_query = "INSERT INTO response (request_id, physician_id, message, timestamp) VALUES (%s, %s, %s, %s)"
                cursor.execute(db_query, (request_id, physician_id, message, timestamp))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    db_query = "UPDATE request SET status=%s WHERE request_id=%s"
                    cursor.execute(db_query, (status, request_id))
                    self.connector.commit()
                    row_count = cursor.rowcount
                    if row_count > -1:
                        if_inserted = True
            except Exception as e:
                print("Add_Physician_Intpr_Response: ", e)
        return if_inserted

    def update_req_and_resp(self, request_id, status, timestamp):
        if_updated = False
        with self.connector.cursor() as cursor:
            try:
                db_query = "UPDATE request AS req LEFT JOIN response AS resp ON req.request_id=resp.request_id SET req.status=%s, req.timestamp=%s, resp.timestamp=%s WHERE req.request_id=%s"
                cursor.execute(db_query, (status, timestamp, timestamp, request_id))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_updated = True
            except Exception as e:
                print("Update_Patient_Request_by_Selection:", e)
        return if_updated



    # KH
    def retrieve_patient_request_list(self, patient_id, time_from=None):
        requests = []
        time_from = int(time_from) if time_from is not None else 0
        db_query = "SELECT request_id, request.timestamp, request.subject, " \
                   "message, medical_image.subject, image_type, level, status " \
                   "FROM miaas.request " \
                   "JOIN miaas.medical_image ON request.image_id = medical_image.image_id " \
                   "WHERE medical_image.user_id=%s and request.timestamp>%s and request.status > 0 " \
                   "ORDER BY request.timestamp DESC"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, (patient_id, time_from))
                self.connector.commit()
                for row in cursor:
                    request = {}
                    request['request_id'] = row[0]
                    request['request_date'] = row[1]
                    request['request_subject'] = row[2]
                    request['message'] = row[3]
                    request['image_subject'] = row[4]
                    request['image_type'] = row[5]
                    request['level'] = row[6]
                    request['status'] = row[7]
                    requests.append(request)
            except Exception as e:
                print("retrieve_patient_request_list: ", e)
        return requests

    # KH
    def retrieve_patient_request_detail(self, request_id):
        request_detail = {}
        responses = []
        db_query_request = "SELECT req.request_id, req.subject, req.message, m.subject, m.image_type, " \
                           "m.timestamp, m.taken_from, m.physician, m.place, m.description, req.status, req.level  " \
                           "FROM miaas.request req " \
                           "JOIN miaas.medical_image m ON req.image_id = m.image_id " \
                           "WHERE req.request_id=%s"

        db_query_response = "SELECT p.user_id, u.name, p.medicine_field, res.message  " \
                            "FROM response res " \
                            "JOIN physician p ON res.physician_id = p.user_id " \
                            "JOIN user u ON p.user_id = u.user_id " \
                            "WHERE res.request_id=%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query_request, request_id)
                self.connector.commit()
                for row in cursor:
                    request_detail['request_id'] = row[0]
                    request_detail['request_subject'] = row[1]
                    request_detail['request_message'] = row[2]
                    request_detail['image_subject'] = row[3]
                    request_detail['image_type'] = row[4]
                    request_detail['image_date'] = row[5]
                    request_detail['taken_from'] = row[6]
                    request_detail['physician_name'] = row[7]
                    request_detail['place'] = row[8]
                    request_detail['description'] = row[9]
                    request_detail['status'] = row[10]
                    request_detail['level'] = row[11]

                cursor.execute(db_query_response, request_id)
                self.connector.commit()
                for row in cursor:
                    response = {}
                    response['physician_id'] = row[0]
                    response['physician_name'] = row[1]
                    response['medicine_filed'] = row[2]
                    response['response_message'] = row[3]
                    responses.append(response)
            except Exception as e:
                print("retrieve_patient_request_detail: ", e)

        return request_detail, responses

    # KH
    def retrieve_requested_intpr_list(self, query_type=None, request_subject=None, image_type=None, physician_id=None, time_from=None):
        requests = []
        time_from = int(time_from) if time_from is not None else 0
        if query_type == "Image Type" and image_type is not None:
            db_query = "SELECT req.request_id, req.timestamp, m.user_id, m.image_type, req.subject, req.status, req.level " \
                       "FROM request req " \
                       "JOIN medical_image m on req.image_id = m.image_id " \
                       "WHERE status >= 2 and image_type='%s' and req.timestamp>%s and '%s' NOT IN(SELECT physician_id FROM response res WHERE req.request_id=res.request_id) " \
                       "ORDER BY status DESC" % (image_type, time_from, physician_id)

        elif query_type == "Request Subject" and request_subject is not None:
            db_query = "SELECT req.request_id, req.timestamp, m.user_id, m.image_type, req.subject, req.status, req.level " \
                       "FROM request req " \
                       "JOIN medical_image m on req.image_id = m.image_id " \
                       "WHERE status >= 2 and req.subject Like '%s' and  req.timestamp>%s and '%s' NOT IN(SELECT physician_id FROM response res WHERE req.request_id=res.request_id) " \
                       "ORDER BY status DESC" % ("%" + request_subject + "%", time_from, physician_id)

        else:
            db_query = "SELECT req.request_id, req.timestamp, m.user_id, m.image_type, req.subject, req.status, req.level " \
                       "FROM request req " \
                       "JOIN medical_image m on req.image_id = m.image_id " \
                       "WHERE status >= 2 and req.timestamp>%s and '%s' NOT IN(SELECT physician_id FROM response res WHERE req.request_id=res.request_id) " \
                       "ORDER BY status DESC" % (time_from, physician_id)
        print(db_query)
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query)
                self.connector.commit()
                for row in cursor:
                    request = {}
                    request['request_id'] = row[0]
                    request['requested_date'] = row[1]
                    request['patient_id'] = row[2]
                    request['image_type'] = row[3]
                    request['request_subject'] = row[4]
                    request['status'] = row[5]
                    request['level'] = row[6]
                    requests.append(request)
            except Exception as e:
                print("Retrieve_Physician_Interpretation: ", e)
        return requests


    # KH
    def retrieve_physician_response_list(self, physician_id):
        responses = []
        db_query = "SELECT req.request_id, req.timestamp, res.timestamp, m.user_id, req.subject, req.message, m.subject, " \
                   "m.image_type, req.level, req.status " \
                   "FROM response res " \
                   "JOIN request req on res.request_id = req.request_id " \
                   "JOIN medical_image m on req.image_id = m.image_id  " \
                   "WHERE res.physician_id = '%s'" \
                   "ORDER BY req.status ASC"%physician_id

        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query)
                self.connector.commit()
                for row in cursor:
                    response = {}
                    response['request_id'] = row[0]
                    response['request_date'] = row[1]
                    response['response_date'] = row[2]
                    response['patient_id'] = row[3]
                    response['request_subject'] = row[4]
                    response['request_message'] = row[5]
                    response['image_subject'] = row[6]
                    response['image_type'] = row[7]
                    response['level'] = row[8]
                    response['status'] = row[9]
                    responses.append(response)
            except Exception as e:
                print("retrieve_patient_request_list: ", e)
        return responses


        # KH
    def retrieve_request_info(self, request_id):
        request_detail = {}
        db_query_request = "SELECT req.request_id, req.subject, req.message, m.subject, m.image_type, " \
                           "m.timestamp, m.taken_from, m.physician, m.place, m.description, req.status, req.level  " \
                           "FROM miaas.request req " \
                           "JOIN miaas.medical_image m ON req.image_id = m.image_id " \
                           "WHERE req.request_id=%s"

        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query_request, request_id)
                self.connector.commit()
                for row in cursor:
                    request_detail['request_id'] = row[0]
                    request_detail['request_subject'] = row[1]
                    request_detail['request_message'] = row[2]
                    request_detail['image_subject'] = row[3]
                    request_detail['image_type'] = row[4]
                    request_detail['image_date'] = row[5]
                    request_detail['taken_from'] = row[6]
                    request_detail['physician_name'] = row[7]
                    request_detail['place'] = row[8]
                    request_detail['description'] = row[9]
                    request_detail['status'] = row[10]
                    request_detail['level'] = row[11]
            except Exception as e:
                print("retrieve_patient_request_detail: ", e)

        return request_detail

    # KH
    def retrieve_interpretation_detail(self, intpr_id):
        intpr_detail = {}
        db_query = "SELECT intpr.intpr_id, intpr.physician_id, u.name, req.level, intpr.summary, intpr.interpretation, " \
                   "m.subject, m.image_type, m.timestamp, " \
                   "m.taken_from, m.physician, m.place, m.description, req.subject, req.message " \
                   "FROM interpretation intpr " \
                   "JOIN physician ph ON intpr.physician_id = ph.user_id " \
                   "JOIN user u ON ph.user_id = u.user_id " \
                   "JOIN request req ON intpr.request_id = req.request_id " \
                   "JOIN medical_image m ON intpr.image_id = m.image_id " \
                   "WHERE intpr.intpr_id =%s"%intpr_id

        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query)
                self.connector.commit()
                for row in cursor:
                    intpr_detail['intpr_id'] = row[0]
                    intpr_detail['physician_id'] = row[1]
                    intpr_detail['physician_name'] = row[2]
                    intpr_detail['level'] = row[3]
                    intpr_detail['summary'] = row[4]
                    intpr_detail['interpretation'] = row[5]
                    intpr_detail['image_subject'] = row[6]
                    intpr_detail['image_type'] = row[7]
                    intpr_detail['image_date'] = row[8]
                    intpr_detail['taken_from'] = row[9]
                    intpr_detail['physician'] = row[10]
                    intpr_detail['place'] = row[11]
                    intpr_detail['description'] = row[12]
                    intpr_detail['request_subject'] = row[13]
                    intpr_detail['request_message'] = row[14]
            except Exception as e:
                print("retrieve_patient_request_detail: ", e)

        return intpr_detail

    # KH
    def retrieve_physician_interpretation_detail(self, intpr_id):
        intpr_detail = {}
        db_query = "SELECT intpr.intpr_id, intpr.physician_id, u.name, req.level, intpr.summary, intpr.interpretation, " \
                   "m.subject, m.image_type, m.timestamp, " \
                   "m.taken_from, m.physician, m.place, m.description, req.subject, req.message " \
                   "FROM interpretation intpr " \
                   "JOIN physician ph ON intpr.physician_id = ph.user_id " \
                   "JOIN user u ON ph.user_id = u.user_id " \
                   "JOIN request req ON intpr.request_id = req.request_id " \
                   "JOIN medical_image m ON intpr.image_id = m.image_id " \
                   "WHERE intpr.intpr_id =%s"%intpr_id

        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query)
                self.connector.commit()
                for row in cursor:
                    intpr_detail['intpr_id'] = row[0]
                    intpr_detail['physician_id'] = row[1]
                    intpr_detail['physician_name'] = row[2]
                    intpr_detail['level'] = row[3]
                    intpr_detail['summary'] = row[4]
                    intpr_detail['interpretation'] = row[5]
                    intpr_detail['image_subject'] = row[6]
                    intpr_detail['image_type'] = row[7]
                    intpr_detail['image_date'] = row[8]
                    intpr_detail['taken_from'] = row[9]
                    intpr_detail['physician'] = row[10]
                    intpr_detail['place'] = row[11]
                    intpr_detail['description'] = row[12]
                    intpr_detail['request_subject'] = row[13]
                    intpr_detail['request_message'] = row[14]
            except Exception as e:
                print("retrieve_patient_request_detail: ", e)

        return intpr_detail

    # KH's
    def retrieve_patient_intpr_list(self, patient_id, time_from=None):
        intprs = []
        time_from = int(time_from) if time_from is not None else 0
        db_query = "SELECT intpr.intpr_id, req.timestamp, intpr.timestamp, req.subject, " \
                   "m.image_type, req.level, intpr.summary " \
                   "FROM interpretation intpr " \
                   "JOIN request req ON intpr.request_id = req.request_id " \
                   "JOIN medical_image m ON intpr.image_id = m.image_id " \
                   "WHERE intpr.patient_id='%s' and intpr.timestamp>%s " \
                   "ORDER BY intpr.timestamp DESC"%(patient_id, time_from)
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query)
                self.connector.commit()
                for row in cursor:
                    intpr = {}
                    intpr['intpr_id'] = row[0]
                    intpr['request_date'] = row[1]
                    intpr['interpret_date'] = row[2]
                    intpr['request_subject'] = row[3]
                    intpr['image_type'] = row[4]
                    intpr['level'] = row[5]
                    intpr['summary'] = row[6]
                    intprs.append(intpr)
            except Exception as e:
                print("retrieve_patient_request_list: ", e)
        return intprs

    # KH
    def retrieve_physician_intpr_list(self, physician_id, time_from=None):
        intprs = []
        time_from = int(time_from) if time_from is not None else 0
        db_query = "SELECT intpr.intpr_id, req.timestamp, intpr.timestamp, req.subject, " \
                   "m.image_type, req.level, intpr.summary " \
                   "FROM interpretation intpr " \
                   "JOIN request req ON intpr.request_id = req.request_id " \
                   "JOIN medical_image m ON intpr.image_id = m.image_id " \
                   "WHERE intpr.physician_id='%s' and intpr.timestamp>%s " \
                   "ORDER BY intpr.timestamp DESC"%(physician_id, time_from)

        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query)
                self.connector.commit()
                for row in cursor:
                    intpr = {}
                    intpr['intpr_id'] = row[0]
                    intpr['request_date'] = row[1]
                    intpr['interpret_date'] = row[2]
                    intpr['request_subject'] = row[3]
                    intpr['image_type'] = row[4]
                    intpr['level'] = row[5]
                    intpr['summary'] = row[6]
                    intprs.append(intpr)
            except Exception as e:
                print("retrieve_patient_request_list: ", e)
        return intprs