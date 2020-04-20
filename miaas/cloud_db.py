import time
import json

from miaas import cloud_db_copy

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
        host = '203.253.21.226'
        user = 'root'
        port = 3306
        password = 'root'
        dbName = 'miaas'
        try:
            self.connector = pymysql.connect(host=host, port=port, user=user, passwd=password, db=dbName,
                                             charset='utf8')
            self.is_connected = True
        except Exception as e:
            logger.exception(e)
            raise Exception("DB Connection Error" + e.message)
            self.is_connected = False

    # HT (for authentication)
    def check_authentication(self, user_id):
        # check the user is need to authenticate
        authenticated = False
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT auth_type FROM authentication WHERE user_id=%s"
                cursor.execute(db_query, user_id)
                row = cursor.fetchone()
                if row:
                    auth_type = row[0]
                    if auth_type != 'new':
                        # already authenticated
                        authenticated = True
                else:
                    # already authenticated
                    authenticated = True
            except Exception as e:
                logger.exception(e)
                authenticated = None
        return authenticated

    def retrieve_authentication(self, user_id, auth_type=None):
        auth = {}
        with self.connector.cursor() as cursor:
            try:
                if auth_type is None:
                    db_query = "SELECT auth_code, auth_type, extra_value FROM authentication WHERE user_id=%s"
                    cursor.execute(db_query, user_id)
                    row = cursor.fetchone()
                    if row:
                        auth['user_id'] = user_id
                        auth['auth_code'] = row[0]
                        auth['auth_type'] = row[1]
                        if row[2]:
                            auth['extra_value'] = row[2]
                    else:
                        return None
                else:
                    db_query = "SELECT auth_code, extra_value FROM authentication WHERE user_id=%s AND auth_type=%s"
                    cursor.execute(db_query, (user_id, auth_type))
                    row = cursor.fetchone()
                    if row:
                        auth['user_id'] = user_id
                        auth['auth_code'] = row[0]
                        auth['auth_type'] = auth_type
                        if row[1]:
                            auth['extra_value'] = row[1]
                    else:
                        return None
            except Exception as e:
                logger.exception(e)
                return None
        return auth

    def add_authentication(self, user_id, auth_code, auth_type='new', extra_value=None):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                if extra_value is None:
                    db_query = "INSERT INTO authentication (user_id, auth_code, auth_type) values (%s, %s, %s)"
                    cursor.execute(db_query, (user_id, auth_code, auth_type))
                else:
                    db_query = "INSERT INTO authentication (user_id, auth_code, auth_type, extra_value)" \
                               " values (%s, %s, %s, %s)"
                    cursor.execute(db_query, (user_id, auth_code, auth_type, extra_value))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
            except Exception as e:
                logger.exception(e)
                raise Exception("Generating authentication failed.")
        return if_inserted

    def update_authentication(self, user_id, auth_code, auth_type='new', extra_value=None):
        is_existed = False

        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT * FROM authentication WHERE user_id=%s"
                cursor.execute(db_query, user_id)
                if cursor.rowcount > 0:
                    is_existed = True
            except:
                pass

        if not is_existed:
            return self.add_authentication(user_id, auth_code, auth_type, extra_value)
        else:
            if_updated = False
            with self.connector.cursor() as cursor:
                try:
                    if extra_value is None:
                        db_query = "UPDATE authentication SET auth_code=%s, auth_type=%s WHERE user_id=%s"
                        cursor.execute(db_query, (auth_code, auth_type, user_id))
                    else:
                        db_query = "UPDATE authentication SET auth_code=%s, auth_type=%s, extra_value=%s" \
                                   " WHERE user_id=%s"
                        cursor.execute(db_query, (auth_code, auth_type, extra_value, user_id))
                    self.connector.commit()
                    row_count = cursor.rowcount
                    if row_count > 0:
                        if_updated = True
                except Exception as e:
                    logger.exception(e)
                    raise Exception("Updating authentication failed.")
            return if_updated

    def delete_authentication(self, user_id, auth_code):
        if_deleted = False
        with self.connector.cursor() as cursor:
            try:
                db_query = "DELETE FROM authentication WHERE user_id=%s AND auth_code=%s"
                cursor.execute(db_query, (user_id, auth_code))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_deleted = True
            except Exception as e:
                logger.exception(e)
                # raise Exception("Deleting authentication failed.")
        return if_deleted

    def check_email(self, user_type, email):
        res = -2
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT user_type FROM user WHERE email=%s"
                cursor.execute(db_query, email)
                if cursor.rowcount > 0:
                    for row in cursor:
                        if row[0] == user_type:
                            res = -1
                            break
                        else:
                            res = 0
                else:
                    res = 1
            except Exception as e:
                logger.exception(e)
                res = -2

        if res >= 0:
            with self.connector.cursor() as cursor2:
                try:
                    db_query = "SELECT u.user_type " \
                               "FROM user as u LEFT JOIN authentication as a on u.user_id=a.user_id " \
                               "WHERE a.extra_value=%s"
                    cursor2.execute(db_query, email)
                    if cursor2.rowcount == 0:
                        pass    # res = res
                    elif cursor2.rowcount > 0:
                        for row in cursor2:
                            if row[0] == user_type:
                                res = -1
                                break
                            else:
                                res = 0
                except Exception as e:
                    logger.exception(e)
                    res = -2
        return res
    # end auth (HT)

    # HT (for changing account info:email and password)
    def change_password(self, user_id, password):
        if_updated = False
        with self.connector.cursor() as cursor:
            try:
                db_query = "UPDATE user SET password=%s WHERE user_id=%s"
                cursor.execute(db_query, (password, user_id))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_updated = True
            except Exception as e:
                logger.exception(e)
                raise Exception("Changing Password failed.")
        return if_updated

    def change_email(self, user_id, email):
        if_updated = False
        with self.connector.cursor() as cursor:
            try:
                db_query = "UPDATE user SET email=%s WHERE user_id=%s"
                cursor.execute(db_query, (email, user_id))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_updated = True
            except Exception as e:
                logger.exception(e)
                raise Exception("Changing Email failed.")
        return if_updated
    # end changing account info (HT)

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
                logger.exception(e)
                raise Exception("Finding existing user is failed.")
        return if_exist

    def retrieve_user_info(self, user_id):
        user = {}
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT first_name, last_name, phone_number, email, user_type " \
                           "FROM user WHERE user_id=%s"
                cursor.execute(db_query, user_id)

                self.connector.commit()
                row = cursor.fetchone()
                user['user_id'] = user_id
                user['first_name'] = row[0]
                user['last_name'] = row[1]
                user['name'] = row[0] + ' ' + row[1]
                user['phone_number'] = row[2]
                user['email'] = row[3]
                user['user_type'] = row[4]

            except Exception as e:
                logger.exception(e)
                raise Exception("Retrieving user information is failed.")
        return user

    def retrieve_user_type(self, user_id, password):
        user_type = None
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT user_type FROM user WHERE user_id=%s and password=%s"
                cursor.execute(db_query, (user_id, password))
                self.connector.commit()
                row = cursor.fetchone()
                user_type = row[0]
            except Exception as e:
                logger.exception(e)
        return user_type

    def find_id(self, email, user_type):
        user_id = None
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT user_id FROM user WHERE email=%s AND user_type=%s"
                cursor.execute(db_query, (email, user_type))
                self.connector.commit()

                if cursor.rowcount > 0:
                    row = cursor.fetchone()
                    user_id = row[0]
                else:
                    raise Exception("There is no matched user information.")
            except Exception as e:
                logger.exception(e)
                raise Exception("Finding ID is failed.")
        return user_id

    def find_passwd(self, user_id, email):
        passwd = None
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT password FROM user WHERE user_id=%s AND email=%s"
                cursor.execute(db_query, (user_id, email))
                self.connector.commit()
                if cursor.rowcount > 0:
                    row = cursor.fetchone()
                    passwd = row[0]
                else:
                    raise Exception("There is no matched user information.")
            except Exception as e:
                logger.exception(e)
                raise Exception("Finding Password is failed.")

        return passwd

    # def reset_passwd(self, user_id, password):
    #     with self.connector.cursor() as cursor:
    #         try:
    #             db_query = "UPDATE user SET password = %s " \
    #                        "WHERE user_id = %s"
    #             cursor.execute(db_query, (password, user_id))
    #             self.connector.commit()
    #             return True
    #         except Exception as e:
    #             logger.exception(e)
    #             return False

    def add_patient(self, patient):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add patient information to 'user' table
                p = patient
                db_query = "INSERT INTO user (user_id, password, first_name, last_name, phone_number, email, " \
                           "birthday, address, city, state, country, user_type, join_date) " \
                           "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query,
                               (p['user_id'], p['password'], p['first_name'], p['last_name'], p['phone_number'], p['email'],
                                p['birthday'], p['address'], p['city'], p['state'], p['country'], p['user_type'], p['join_date']))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
                else:
                    if_inserted = False
                    raise Exception("Cannot Inserted.")

                # Add patient information to 'user' table
                db_query = "INSERT INTO patient (user_id, gender) VALUES (%s, %s)"
                cursor.execute(db_query, (p['user_id'], p['gender']))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
                else:
                    if_inserted = False
                    db_query = "DELETE FROM user WHERE user_id=%s"
                    cursor.execute(db_query, p['user_id'])
                    self.connector.commit()
            except Exception as e:
                logger.exception(e)
                raise Exception("Registering a patient is failed.")
        return if_inserted

    def retrieve_patient(self, patient_id, password=None):
        user = {}
        with self.connector.cursor() as cursor:
            try:
                if password is None:
                    db_query = "SELECT u.first_name, u.last_name, u.phone_number, u.email, u.birthday," \
                               "u.address, u.city, u.state, u.country, u.user_type, u.join_date, u.deactivate_date, " \
                               "p.gender " \
                               "FROM patient as p LEFT JOIN user as u on p.user_id=u.user_id " \
                               "WHERE u.user_id=%s"
                    cursor.execute(db_query, patient_id)
                else:
                    db_query = "SELECT u.first_name, u.last_name, u.phone_number, u.email, u.birthday," \
                               "u.address, u.city, u.state, u.country, u.user_type, u.join_date, u.deactivate_date, " \
                               "p.gender, u.password " \
                               "FROM patient as p LEFT JOIN user as u on p.user_id=u.user_id " \
                               "WHERE u.user_id=%s and u.password=%s"
                    cursor.execute(db_query, (patient_id, password))
                for row in cursor:
                    user['user_id'] = patient_id
                    user['first_name'] = row[0]
                    user['last_name'] = row[1]
                    user['name'] = row[0] + ' ' + row[1]
                    user['phone_number'] = row[2]
                    user['email'] = row[3]
                    user['birthday'] = row[4]
                    user['address'] = row[5]
                    user['city'] = row[6]
                    user['state'] = row[7]
                    user['country'] = row[8]
                    user['user_type'] = row[9]
                    user['join_date'] = row[10]
                    user['deactivate_date'] = row[11]
                    user['gender'] = row[12]
                    if password is None:
                        user['password'] = None
                    else:
                        user['password'] = row[13]
            except Exception as e:
                logger.exception(e)
                raise Exception("Login is Failed.")
        return user

    def update_patient(self, user):
        if_updated = False
        with self.connector.cursor() as cursor:
            try:
                p = user
                db_query = "UPDATE user as u INNER JOIN patient as p ON u.user_id=p.user_id " \
                           "SET u.password=%s, u.first_name=%s, u.last_name=%s, u.phone_number=%s, u.email=%s, " \
                           "u.birthday=%s, u.address=%s, u.city=%s, u.state=%s, u.country=%s, " \
                           "p.gender=%s " \
                           "WHERE u.user_id=%s"
                cursor.execute(db_query, (p['password'], p['first_name'], p['last_name'], p['phone_number'], p['email'],
                                          p['birthday'], p['address'], p['city'], p['state'], p['country'],
                                          p['gender'], p['user_id']))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_updated = True
            except Exception as e:
                logger.exception(e)
                raise Exception("Updating user information is failed.")
        return if_updated

    ### old ###
    # def add_patient_profile(self, user_id, timestamp, profiles):
    #     if_inserted = False
    #     # Build an insert query
    #     db_query = "INSERT INTO patient_profile (user_id, type, value, timestamp) VALUES (%s, %s, %s, %s)"
    #     items = []
    #     for prof in profiles:
    #         items.append((user_id, prof['type'], prof['value'], timestamp))
    #     with self.connector.cursor() as cursor:
    #         try:
    #             cursor.executemany(db_query, items)
    #             self.connector.commit()
    #             row_count = cursor.rowcount
    #             if row_count > 0:
    #                 if_inserted = True
    #         except Exception as e:
    #             logger.exception(e)
    #             raise Exception("Updating patient profile is failed.")
    #     return if_inserted

    def update_patient_profile(self, user_id, profiles):
        profiles['user_id'] = user_id
        if_basic_updated = False

        logger.info(profiles)
        db_query = "INSERT INTO patient_profile_basic " \
                   "(user_id, height, weight, drinkingCapacity, drinkingFrequency, " \
                   "sleeping, exercise, smoking, water) " \
                   "VALUES (%(user_id)s, %(height)s, %(weight)s, %(drinkingCapacity)s, %(drinkingFrequency)s, " \
                   "%(sleeping)s, %(exercise)s, %(smoking)s, %(water)s) " \
                   "ON DUPLICATE KEY UPDATE height=%(height)s, weight=%(weight)s, " \
                   "drinkingCapacity=%(drinkingCapacity)s, drinkingFrequency=%(drinkingFrequency)s, " \
                   "sleeping=%(sleeping)s, exercise=%(exercise)s, smoking=%(smoking)s, water=%(water)s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, profiles)
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_basic_updated = True
            except Exception as e:
                logger.exception(e)
                raise Exception("Updating patient profile error.")

        if not profiles.get('detail'):
            return if_basic_updated

        profiles['detail']['user_id'] = user_id
        if_detail_updated = False

        db_query = "INSERT INTO patient_profile_detail " \
                   "(user_id, pmh, ed, sd, med, fmh, alg, notice)" \
                   "VALUES (%(user_id)s, %(pmh)s, %(ed)s, %(sd)s, %(med)s, %(fmh)s, %(alg)s, %(notice)s) " \
                   "ON DUPLICATE KEY UPDATE pmh=%(pmh)s, ed=%(ed)s, sd=%(sd)s, med=%(med)s, " \
                   "fmh=%(fmh)s, alg=%(alg)s, notice=%(notice)s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, profiles['detail'])
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_detail_updated = True
            except Exception as e:
                logger.exception(e)
                raise Exception("Updating patient profile error.")
        return if_basic_updated or if_detail_updated


    # type='None' (performance low)
    def retrieve_patient_profile(self, patient_id):
        profiles = {}
        db_query = "SELECT height, weight, drinkingCapacity, drinkingFrequency, sleeping, exercise, smoking, water, " \
                   "pmh, ed, sd, med, fmh, alg, notice " \
                   "FROM patient_profile_all "  \
                   "WHERE user_id=%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, patient_id)
                row = cursor.fetchone()
                if row:
                    profiles['height'] = row[0]
                    profiles['weight'] = row[1]
                    profiles['drinkingCapacity'] = row[2]
                    profiles['drinkingFrequency'] = row[3]
                    profiles['sleeping'] = row[4]
                    profiles['exercise'] = row[5]
                    profiles['smoking'] = row[6]
                    profiles['water'] = row[7]
                    profiles['detail'] = {}
                    profiles['detail']['pmh'] = row[8]
                    profiles['detail']['ed'] = row[9]
                    profiles['detail']['sd'] = row[10]
                    profiles['detail']['med'] = row[11]
                    profiles['detail']['fmh'] = row[12]
                    profiles['detail']['alg'] = row[13]
                    profiles['detail']['notice'] = row[14]
            except Exception as e:
                logger.exception(e)
                raise Exception("Retrieve patient profile error.")
        return profiles

    def add_physician(self, physician):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add physician information to 'user' table
                p = physician
                db_query = "INSERT INTO user (user_id, password, first_name, last_name, phone_number, email, " \
                           "birthday, address, city, state, country, user_type, join_date) " \
                           "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query,
                               (p['user_id'], p['password'], p['first_name'], p['last_name'], p['phone_number'], p['email'],
                                p['birthday'], p['address'], p['city'], p['state'], p['country'], p['user_type'], p['join_date']))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
                else:
                    if_inserted = False
                    raise Exception("Cannot Inserted.")

                # Add physician information to 'physician' table
                db_query = "INSERT INTO physician (user_id, license_number, medicine_field, certificate_dir) " \
                           "values (%s, %s, %s, %s)"
                cursor.execute(db_query, (p['user_id'], p['license_number'], p['medicine_field'], p['certificate_dir']))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
                else:
                    if_inserted = False
                    db_query = "DELETE FROM user WHERE user_id=%s"
                    cursor.execute(db_query, p['user_id'])
                    self.connector.commit()

                # Add physician_profile information
                db_query = "INSERT INTO physician_profile (user_id) values (%s)"
                cursor.execute(db_query, p['user_id'])
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
                else:
                    if_inserted = False
                    db_query = "DELETE FROM user WHERE user_id=%s"
                    cursor.execute(db_query, p['user_id'])
                    self.connector.commit()
                    db_query = "DELETE FROM physician WHERE user_id=%s"
                    cursor.execute(db_query, p['user_id'])
                    self.connector.commit()

            except Exception as e:
                logger.exception(e)
                raise Exception("Registering a physician is failed.")
        return if_inserted

    def retrieve_physician(self, physician_id, password=None):
        user = {}
        with self.connector.cursor() as cursor:
            try:
                if password is None:
                    db_query = "SELECT u.first_name, u.last_name, u.phone_number, u.email, u.birthday," \
                               "u.address, u.city, u.state, u.country, u.user_type, u.join_date, u.deactivate_date, " \
                               "p.license_number, p.medicine_field, p.certificate_dir " \
                               "FROM physician as p LEFT JOIN user as u on p.user_id=u.user_id " \
                               "WHERE u.user_id=%s"
                    cursor.execute(db_query, physician_id)
                else:
                    db_query = "SELECT u.first_name, u.last_name, u.phone_number, u.email, u.birthday," \
                               "u.address, u.city, u.state, u.country, u.user_type, u.join_date, u.deactivate_date, " \
                               "p.license_number, p.medicine_field, p.certificate_dir, u.password " \
                               "FROM physician as p LEFT JOIN user as u on p.user_id=u.user_id " \
                               "WHERE u.user_id=%s and u.password=%s"
                    cursor.execute(db_query, (physician_id, password))
                self.connector.commit()
                for row in cursor:
                    user['user_id'] = physician_id
                    user['first_name'] = row[0]
                    user['last_name'] = row[1]
                    user['name'] = row[0] + ' ' + row[1]
                    user['phone_number'] = row[2]
                    user['email'] = row[3]
                    user['birthday'] = row[4]
                    user['address'] = row[5]
                    user['city'] = row[6]
                    user['state'] = row[7]
                    user['country'] = row[8]
                    user['user_type'] = row[9]
                    user['join_date'] = row[10]
                    user['deactivate_date'] = row[11]
                    user['license_number'] = row[12]
                    user['medicine_field'] = row[13]
                    user['certificate_dir'] = row[14]
                    if password is None:
                        user['password'] = None
                    else:
                        user['password'] = row[15]
            except Exception as e:
                logger.exception(e)
                raise Exception("Login is failed.")
        return user

    def update_physician(self, user):
        if_updated = False
        with self.connector.cursor() as cursor:
            try:
                p = user
                db_query = "UPDATE user as u INNER JOIN physician as p ON u.user_id=p.user_id " \
                           "SET u.password=%s, u.first_name=%s, u.last_name=%s, u.phone_number=%s, u.email=%s, " \
                           "u.birthday=%s, u.address=%s, u.city=%s, u.state=%s, u.country=%s, " \
                           "p.license_number=%s, p.medicine_field=%s, p.certificate_dir=%s " \
                           "WHERE u.user_id=%s"
                cursor.execute(db_query, (p['password'], p['first_name'], p['last_name'], p['phone_number'], p['email'],
                                          p['birthday'], p['address'], p['city'], p['state'], p['country'],
                                          p['license_number'], p['medicine_field'], p['certificate_dir'], p['user_id']))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_updated = True
            except Exception as e:
                logger.exception(e)
                raise Exception("Updating user information is failed.")
        return if_updated

    # def add_physician_profile(self, user_id, keys, values):
    #     if_updated = False
    #     db_query = "UPDATE physician_profile SET "
    #     for key in keys:
    #         if key is keys[-1]:
    #             db_query = db_query + key + '=%s '
    #         else:
    #             db_query = db_query + key + '=%s, '
    #     db_query = db_query + "WHERE user_id='" + user_id + "'"
    #     with self.connector.cursor() as cursor:
    #         try:
    #             cursor.execute(db_query, tuple(values))
    #             self.connector.commit()
    #             row_count = cursor.rowcount
    #             if row_count > 0:
    #                 if_updated = True
    #             return if_updated
    #         except Exception as e:
    #             logger.exception(e)
    #             raise Exception( "add_physician_profile Error" + e.message)
    #     return if_updated

    def add_physician_profile(self, user_id, keys, values):
        if_updated = False
        db_query = "INSERT INTO physician_profile_copy VALUES (%s, %s, %s) ON  DUPLICATE KEY UPDATE " \
                   "user_id = VALUES(user_id), " \
                   "type = values(type)," \
                   "value = values(VALUE) "
        temp = []
        for k in keys:
            temp.append(user_id)
        parameters = zip(temp, keys, values)
        with self.connector.cursor() as cursor:
            try:
                cursor.executemany(db_query, parameters)
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_updated = True
                return if_updated
            except Exception as e:
                logger.exception(e)
                raise Exception("Updating physician profile is failed.")
        return if_updated

    # def retrieve_physician_profile(self, physician_id, type=None):
    #     profile = {}
    #     with self.connector.cursor() as cursor:
    #         try:
    #             db_query = "SELECT * FROM physician_profile WHERE user_id=%s"
    #             cursor.execute(db_query, physician_id)
    #             self.connector.commit()
    #             for row in cursor:
    #                 profile['user_id'] = row[0]
    #                 profile['aboutMe'] = row[1]
    #                 profile['specialism'] = row[2]
    #                 profile['medicalSchool'] = row[3]
    #                 profile['graduate'] = row[4]
    #                 profile['certifications'] = row[5]
    #                 profile['memberships'] = row[6]
    #                 profile['fieldsOfMedicine'] = row[7]
    #                 profile['hiv'] = row[8]
    #                 profile['offices'] = row[9]
    #                 profile['languages'] = row[10]
    #                 profile['insuranceProgram'] = row[11]
    #                 profile['healthPlans'] = row[12]
    #                 profile['hospitalPrivileges'] = row[13]
    #                 profile['malpractice'] = row[14]
    #                 profile['licenseeActions'] = row[15]
    #                 profile['outOfStateActions'] = row[16]
    #                 profile['currentLimits'] = row[17]
    #                 profile['hspPrivRestrictions'] = row[18]
    #                 profile['hspFRPriv'] = row[19]
    #                 profile['criminalConvictions'] = row[20]
    #                 profile['teaching'] = row[21]
    #                 profile['serviceActivity'] = row[22]
    #                 profile['publications'] = row[23]
    #                 profile['statement'] = row[24]
    #         except Exception as e:
    #             logger.exception(e)
    #             raise Exception( "Retrieve retrieve_physician_profile Profile Error" + e.message)
    #     return profile

    def retrieve_physician_profile(self, physician_id, type=None):
        profile = {}
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT * FROM physician_profile_copy WHERE user_id=%s"
                cursor.execute(db_query, physician_id)
                self.connector.commit()
                for row in cursor:
                    profile[row[1]] = row[2]
            except Exception as e:
                logger.exception(e)
                raise Exception("Unknown error occurs while getting the physician profile information.")
        return profile

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
                image_dir = medical_image['image_dir']
                # image_dir = 'DUMMY_DIR'
                # size = medical_image['size']
                timestamp = medical_image['timestamp']
                taken_date = medical_image['taken_date']
                medical_department = medical_image['medical_department']
                db_query = "INSERT INTO medical_image (user_id, subject, image_type, taken_from, physician, place, description, image_dir, timestamp, taken_date, medical_department) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query, (
                    user_id, subject, image_type, taken_from, physician, place, description, image_dir, timestamp,
                    taken_date, medical_department))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
            except Exception as e:
                logger.exception(e)
                raise Exception("Uploading a medical image is failed.")

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
        taken_date = medical_image['taken_date']
        medical_department = medical_image['medical_department']

        with self.connector.cursor() as cursor:
            try:
                db_query = "UPDATE medical_image SET subject=%s, image_type=%s, taken_from=%s, physician=%s, place=%s, description=%s, taken_date=%s, medical_department=%s WHERE image_id=%s"
                cursor.execute(db_query,
                               (subject, image_type, taken_from, physician, place, description, taken_date,
                                medical_department, image_id))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_updated = True
            except Exception as e:
                logger.exception(e)
                raise Exception("Updating medical image information is failed.")

        return if_updated

    def retrieve_medical_image(self, user_id, time_from=None, offset=None, limit=None):
        images = []
        time_from = int(time_from) if time_from is not None else 0
        offset = int(offset) if offset is not None else 0
        limit = int(limit) if limit is not None else 0
        with self.connector.cursor() as cursor:
            try:
                if limit is 0:
                    db_query = "SELECT image_id, user_id, subject, image_type, taken_from, " \
                               "physician, place, description, image_dir, size, timestamp, intpr_num, " \
                               "taken_date, medical_department FROM medical_image " \
                               "WHERE user_id=%s and timestamp>=%s ORDER BY timestamp DESC"
                    cursor.execute(db_query, (user_id, time_from))
                else:
                    db_query = "SELECT image_id, user_id, subject, image_type, taken_from, " \
                               "physician, place, description, image_dir, size, timestamp, intpr_num, " \
                               "taken_date, medical_department FROM medical_image " \
                               "WHERE user_id=%s and timestamp>=%s ORDER BY timestamp DESC LIMIT %s OFFSET %s"
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
                    image['taken_date'] = row[12]
                    image['medical_department'] = row[13]
                    images.append(image)
            except Exception as e:
                logger.exception(e)
                raise Exception("Unknown error occurs while collectting your medical images")
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
                logger.exception(e)
                raise Exception("retrieve_medical_image_amount Error" + e.message)
        return amount

    def retrieve_medical_image_by_id(self, image_id):
        db_query = "SELECT image_id, user_id, subject, image_type, taken_from, " \
                   "physician, place, description, image_dir, size, timestamp, intpr_num, " \
                   "taken_date, medical_department FROM medical_image WHERE image_id=%s"
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
                image['taken_date'] = row[12]
                image['medical_department'] = row[13]
            except Exception as e:
                logger.exception(e)
                raise Exception("Unknown error occurs while getting the medical image information.")
        return image

    def update_medical_image_dir(self, medical_image):
        if_updated = False
        image_dir = medical_image['image_dir']
        image_id = medical_image['image_id']
        with self.connector.cursor() as cursor:
            try:
                db_query = "UPDATE medical_image SET image_dir=%s WHERE image_id=%s"
                cursor.execute(db_query, (image_dir, image_id))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_updated = True
            except Exception as e:
                logger.exception(e)
                raise Exception("Updating medical image is failed")
        return if_updated

    def update_medical_image_intprnum(self, image_id):
        if_updated = False
        with self.connector.cursor() as cursor:
            try:
                db_query = "UPDATE medical_image SET intpr_num=intpr_num+1 WHERE image_id=%s"
                cursor.execute(db_query, (image_id))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_updated = True
            except Exception as e:
                logger.exception(e)
                raise Exception("Updating interpretation is failed.")
        return if_updated

    def delete_medical_image_by_id(self, image_id):
        if_deleted = False
        with self.connector.cursor() as cursor:
            try:
                db_query = "DELETE FROM medical_image WHERE image_id=%s"
                cursor.execute(db_query, (image_id))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_deleted = True
            except Exception as e:
                logger.exception(e)
                raise Exception("Deleting a medical image is failed")
        return if_deleted

    def temp_save_intpr(self, intpr):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                request_id = intpr['request_id']
                summary = intpr['summary']
                suspected_disease = intpr['suspected_disease']
                opinion = intpr['opinion']
                recommendation = intpr['recommendation']

                db_query = "INSERT INTO interpretation_temp VALUES (%s, %s, %s, %s, %s) " \
                           "ON  DUPLICATE KEY UPDATE " \
                           "request_id = values(request_id), " \
                           "summary = values(summary), " \
                           "suspected_disease = values(suspected_disease), " \
                           "opinion = values(opinion), " \
                           "recommendation = values(recommendation) "

                cursor.execute(db_query, (request_id, summary, suspected_disease, opinion, recommendation))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True

            except Exception as e:
                logger.exception(e)
                raise Exception("The interpretation is not saved.")
        return if_inserted

    def delete_temp_intpr(self, request_id):
        if_deleted = False
        with self.connector.cursor() as cursor:
            try:
                db_query = "DELETE FROM interpretation_temp " \
                           "WHERE request_id = %s"
                cursor.execute(db_query, request_id)
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_deleted = True
            except Exception as e:
                pass
        return if_deleted

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
                request_id = intpr['request_id']
                suspected_disease = intpr['suspected_disease']
                opinion = intpr['opinion']
                recommendation = intpr['recommendation']
                db_query = "INSERT INTO interpretation " \
                           "(patient_id, physician_id, image_id, level, " \
                           "fee, timestamp, summary, request_id, " \
                           "suspected_disease, opinion, recommendation) " \
                           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(db_query, (patient_id, physician_id, image_id, level,
                                          fee, timestamp, summary, request_id,
                                          suspected_disease, opinion, recommendation))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_inserted = True
            except Exception as e:
                logger.exception(e)
                raise Exception("Unknown error occurs while committing the interpretation")
        return if_inserted

    def retrieve_intpr_by_id(self, intpr_id):
        db_query = "SELECT intpr_id, patient_id, physician_id, image_id, " \
                   "level, fee, timestamp, summary, request_id, " \
                   "suspected_disease, opinion, recommendation FROM interpretation " \
                   "WHERE intpr_id=%s"
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
                intpr['request_id'] = row[8]
                intpr['suspected_disease'] = row[9]
                intpr['opinion'] = row[10]
                intpr['recommendation'] = row[11]

            except Exception as e:
                logger.exception(e)
                raise Exception("Unknown error occurs while getting the information of the interpretation")
        return intpr

    # To retrieve all interpretation information from 'interpretation' table on 'image_id' arguments with medical image information from 'medical_image'
    def retrieve_image_and_intpr(self, image_id):
        intpr_by_image = {}
        intpr_list = []
        with self.connector.cursor() as cursor:
            try:
                # To retrieve data from 'medical_image' table
                intpr_by_image['image'] = self.retrieve_medical_image_by_id(image_id)
                # To retrieve data from 'interpretation' table
                db_query = "SELECT i.intpr_id, i.patient_id, i.physician_id, i.image_id, " \
                           "i.level, i.fee, i.timestamp, i.summary, i.request_id, " \
                           "i.suspected_disease, i.opinion, i.recommendation, " \
                           "p.first_name, p.last_name " \
                           "FROM interpretation as i LEFT JOIN user p ON i.physician_id = p.user_id " \
                           "WHERE image_id=%s"
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
                    intpr['request_id'] = row[8]
                    intpr['suspected_disease'] = row[9]
                    intpr['opinion'] = row[10]
                    intpr['recommendation'] = row[11]
                    intpr['physician_first_name'] = row[12]
                    intpr['physician_last_name'] = row[13]
                    intpr['physician_name'] = row[12] + ' ' + row[13]
                    intpr_list.append(intpr)
                intpr_by_image['intpr'] = intpr_list
            except Exception as e:
                logger.exception(e)
                raise Exception(
                    "Unknown error occurs while the information of interpretation related to the medical image.")
        return intpr_by_image

    def retrieve_image_intpr(self, image_id, time_from=None, offset=None, limit=None):
        intprs = []
        time_from = int(time_from) if time_from is not None else 0
        offset = int(offset) if offset is not None else 0
        limit = int(limit) if limit is not None else 0
        with self.connector.cursor() as cursor:
            if limit is 0:
                db_query = "SELECT intpr_id, patient_id, physician_id, image_id, " \
                           "level, fee, timestamp, summary, request_id, " \
                           "suspected_disease, opinion, recommendation FROM interpretation WHERE image_id=%s and timestamp>%s ORDER BY timestamp DESC"
                cursor.execute(db_query, (image_id, time_from))
            else:
                db_query = "SELECT intpr_id, patient_id, physician_id, image_id, " \
                           "level, fee, timestamp, summary, request_id, " \
                           "suspected_disease, opinion, recommendation FROM interpretation WHERE image_id=%s and timestamp>%s ORDER BY timestamp DESC LIMIT %s OFFSET %s"
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
                    intpr['request_id'] = row[8]
                    intpr['suspected_disease'] = row[9]
                    intpr['opinion'] = row[10]
                    intpr['recommendation'] = row[11]

                    intprs.append(intpr)
            except Exception as e:
                logger.exception(e)
                raise Exception(
                    "Unknown error occurs while the information of interpretation related to the medical image.")
        return intprs

    def retrieve_physician_intpr(self, physician_id, time_from=None):
        intprs = []
        time_from = int(time_from) if time_from is not None else 0
        db_query = "SELECT intpr_id, patient_id, physician_id, image_id, " \
                   "level, fee, timestamp, summary, request_id, " \
                   "suspected_disease, opinion, recommendation FROM interpretation WHERE physician_id=%s and timestamp>%s ORDER BY timestamp DESC"
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
                    intpr['request_id'] = row[8]
                    intpr['suspected_disease'] = row[9]
                    intpr['opinion'] = row[10]
                    intpr['recommendation'] = row[11]

                    intprs.append(intpr)
            except Exception as e:
                logger.exception(e)
                raise Exception("Unknown error occurs while your interpretations.")
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
                logger.exception(e)
                raise Exception("retrieve_physician_intpr_amount Error" + e.message)
        return amount

    def retrieve_patient_intpr(self, patient_id, time_from=None):
        intprs = []
        time_from = int(time_from) if time_from is not None else 0
        db_query = "SELECT intpr_id, patient_id, physician_id, image_id, " \
                   "level, fee, timestamp, summary, request_id, " \
                   "suspected_disease, opinion, recommendation FROM interpretation WHERE patient_id=%s and timestamp>%s ORDER BY timestamp DESC"
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
                    intpr['request_id'] = row[8]
                    intpr['suspected_disease'] = row[9]
                    intpr['opinion'] = row[10]
                    intpr['recommendation'] = row[11]

                    intprs.append(intpr)
            except Exception as e:
                logger.exception(e)
                raise Exception("Unknown error occurs while your interpretations.")
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
                logger.exception(e)
                raise Exception("retrieve_patient_intpr_amount Error" + e.message)
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
                logger.exception(e)
                raise Exception("Unknown error occurs while your requests.")
        return if_inserted

    def update_patient_request_by_selection(self, request_id, physician_id, status):
        if_updated = False
        with self.connector.cursor() as cursor:
            try:
                db_query = "UPDATE request SET status=%s WHERE request_id=%s"
                cursor.execute(db_query, (status, request_id))
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
                logger.exception(e)
                raise Exception("Selection a physician is failed.")
        return if_updated

    def update_patient_request(self, request_id, subject, message, timestamp):
        if_updated = False
        with self.connector.cursor() as cursor:
            try:
                db_query = "UPDATE request SET subject=%s, message=%s WHERE request_id=%s"
                subject = subject
                message = message
                cursor.execute(db_query, (subject, message, request_id))
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_updated = True
            except Exception as e:
                logger.exception(e)
                raise Exception("Unknown error occurs during the request-response transaction.")
        return if_updated

    def delete_patient_request(self, request_id):
        if_deleted = False
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT req.request_id, m.user_id, res.physician_id, req.subject " \
                           "FROM request req " \
                           "JOIN response res ON req.request_id = res.request_id " \
                           "JOIN medical_image m ON req.image_id = m.image_id " \
                           "WHERE req.request_id = %s"

                cursor.execute(db_query, request_id)
                for row in cursor:
                    value = {
                        "request_subject": row[3]
                    }
                    self.add_session(row[1], row[2], 'cancel', json.dumps(value), int(round(time.time() * 1000)))

                db_query = "DELETE FROM request WHERE request_id=%s"
                cursor.execute(db_query, request_id)
                self.connector.commit()
                row_count = cursor.rowcount
                if row_count > 0:
                    if_deleted = True

            except Exception as e:
                logger.exception(e)
                raise Exception("Canceling the request is failed.")
        return if_deleted

    def add_physician_intpr_resp(self, response):
        if_inserted = False
        with self.connector.cursor() as cursor:
            try:
                # Add response information to 'response' table
                request_id = response['request_id']
                physician_id = response['physician_id']
                message = response['message']
                # message = respo.encode('utf-8').decode('latin-1')nse['message']
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
                logger.exception(e)
                raise Exception(Exception("Responsing the request is failed."))
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
                logger.exception(e)
                raise Exception("Unknown error occurs during the request-response transaction.")
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
                logger.exception(e)
                raise Exception("retrieve_patient_request_list Error" + e.message)
        return requests

    # KH
    def retrieve_patient_request_detail(self, request_id):
        request_detail = {}
        responses = []
        db_query_request = "SELECT req.request_id, req.subject, req.message, m.subject, m.image_type, " \
                           "m.timestamp, m.taken_from, m.physician, m.place, m.description, req.status, req.level, m.image_id  " \
                           "FROM miaas.request req " \
                           "JOIN miaas.medical_image m ON req.image_id = m.image_id " \
                           "WHERE req.request_id=%s"

        db_query_response = "SELECT p.user_id, u.first_name, u.last_name, p.medicine_field, res.message  " \
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
                    request_detail['image_id'] = row[12]

                cursor.execute(db_query_response, request_id)
                self.connector.commit()
                for row in cursor:
                    response = {}
                    response['physician_id'] = row[0]
                    response['physician_name'] = row[1] + ' ' + row[2]
                    response['medicine_filed'] = row[3]
                    response['response_message'] = row[4]
                    responses.append(response)
            except Exception as e:
                logger.exception(e)
                raise Exception("retrieve_patient_request_detail Error" + e.message)

        return request_detail, responses

    # KH
    def retrieve_requested_intpr_list(self, query_type=None, request_subject=None, image_type=None, physician_id=None,
                                      time_from=None):
        requests = []
        time_from = int(time_from) if time_from is not None else 0
        if query_type == "Image Type" and image_type is not None:
            db_query = "SELECT req.request_id, req.timestamp, m.user_id, m.image_type, req.subject, req.status, req.level, m.subject " \
                       "FROM request req " \
                       "JOIN medical_image m on req.image_id = m.image_id " \
                       "WHERE status >= 2 and image_type='%s' and req.timestamp>%s and '%s' NOT IN(SELECT physician_id FROM response res WHERE req.request_id=res.request_id) " \
                       "ORDER BY req.timestamp DESC" % (image_type, time_from, physician_id)

        elif query_type == "Request Subject" and request_subject is not None:
            db_query = "SELECT req.request_id, req.timestamp, m.user_id, m.image_type, req.subject, req.status, req.level, m.subject " \
                       "FROM request req " \
                       "JOIN medical_image m on req.image_id = m.image_id " \
                       "WHERE status >= 2 and req.subject Like '%s' and  req.timestamp>%s and '%s' NOT IN(SELECT physician_id FROM response res WHERE req.request_id=res.request_id) " \
                       "ORDER BY req.timestamp DESC" % ("%" + request_subject + "%", time_from, physician_id)

        else:
            db_query = "SELECT req.request_id, req.timestamp, m.user_id, m.image_type, req.subject, req.status, req.level, m.subject " \
                       "FROM request req " \
                       "JOIN medical_image m on req.image_id = m.image_id " \
                       "WHERE status >= 2 and req.timestamp>%s and '%s' NOT IN(SELECT physician_id FROM response res WHERE req.request_id=res.request_id) " \
                       "ORDER BY req.timestamp DESC" % (time_from, physician_id)
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
                    request['image_subject'] = row[7]
                    requests.append(request)
            except Exception as e:
                logger.exception(e)
                raise Exception("retrieve_requested_intpr_list Error" + e.message)
        return requests

    # KH
    def retrieve_physician_response_list(self, physician_id):
        responses = []
        db_query = "SELECT req.request_id, req.timestamp, res.timestamp, m.user_id, req.subject, req.message, m.subject, " \
                   "m.image_type, req.level, req.status " \
                   "FROM response res " \
                   "JOIN request req on res.request_id = req.request_id " \
                   "JOIN medical_image m on req.image_id = m.image_id  " \
                   "WHERE res.physician_id = '%s' and req.status > 0 " \
                   "ORDER BY " \
                   "CASE " \
                   "WHEN req.status = 1 Then 3 " \
                   "WHEN req.status = 2 Then 2 " \
                   "WHEN req.status = 0 Then 0 " \
                   "END DESC" % physician_id

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
                logger.exception(e)
                raise Exception("retrieve_physician_response_list Error" + e.message)
        return responses

    # KH
    def retrieve_request_info(self, request_id):
        request_detail = {}
        db_query_request = "SELECT req.request_id, req.subject, req.message, m.subject, m.image_type, " \
                           "m.timestamp, m.taken_from, m.physician, m.place, m.description, " \
                           "req.status, req.level, m.user_id, m.image_id, " \
                           "u.first_name, u.last_name, u.phone_number, u.email " \
                           "FROM miaas.request req " \
                           "JOIN miaas.medical_image m ON req.image_id = m.image_id " \
                           "JOIN miaas.user u ON m.user_id = u.user_id " \
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
                    request_detail['patient_id'] = row[12]
                    request_detail['image_id'] = row[13]
                    request_detail['name'] = row[14] + ' ' + row[15]
                    request_detail['phone_number'] = row[16]
                    request_detail['email'] = row[17]

            except Exception as e:
                logger.exception(e)
                raise Exception("retrieve_request_info Error" + e.message)

        return request_detail

    # KH
    def retrieve_interpretation_detail(self, intpr_id):
        intpr_detail = {}
        db_query = "SELECT intpr.intpr_id, intpr.physician_id, u.first_name, u.last_name, req.level, intpr.summary, " \
                   "intpr.suspected_disease, intpr.opinion, intpr.recommendation, " \
                   "m.subject, m.image_type, m.timestamp, m.medical_department, " \
                   "m.taken_from, m.physician, m.place, m.description, req.subject, req.message, m.image_id " \
                   "FROM interpretation intpr " \
                   "JOIN physician ph ON intpr.physician_id = ph.user_id " \
                   "JOIN user u ON ph.user_id = u.user_id " \
                   "JOIN request req ON intpr.request_id = req.request_id " \
                   "JOIN medical_image m ON intpr.image_id = m.image_id " \
                   "WHERE intpr.intpr_id =%s" % intpr_id

        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query)
                self.connector.commit()
                for row in cursor:
                    intpr_detail['intpr_id'] = row[0]
                    intpr_detail['physician_id'] = row[1]
                    intpr_detail['physician_name'] = row[2] + ' ' + row[3]
                    intpr_detail['level'] = row[4]
                    intpr_detail['summary'] = row[5]
                    intpr_detail['suspected_disease'] = row[6]
                    intpr_detail['opinion'] = row[7]
                    intpr_detail['recommendation'] = row[8]
                    intpr_detail['image_subject'] = row[9]
                    intpr_detail['image_type'] = row[10]
                    intpr_detail['image_date'] = row[11]
                    intpr_detail['medical_department'] = row[12]
                    intpr_detail['taken_from'] = row[13]
                    intpr_detail['physician'] = row[14]
                    intpr_detail['place'] = row[15]
                    intpr_detail['description'] = row[16]
                    intpr_detail['request_subject'] = row[17]
                    intpr_detail['request_message'] = row[18]
                    intpr_detail['image_id'] = row[19]
            except Exception as e:
                logger.exception(e)
                raise Exception("retrieve_interpretation_detail Error" + e.message)

        return intpr_detail

    # KH
    def retrieve_physician_interpretation_detail(self, intpr_id):
        intpr_detail = {}
        db_query = "SELECT intpr.intpr_id, intpr.physician_id, u.first_name, u.last_name, req.level, intpr.summary, " \
                   "intpr.suspected_disease, intpr.opinion, intpr.recommendation, " \
                   "m.subject, m.image_type, m.timestamp, m.medical_department, " \
                   "m.taken_from, m.physician, m.place, m.description, req.subject, req.message, m.image_id, " \
                   "m.user_id, pa.name, pa.email, pa.phone_number " \
                   "FROM interpretation intpr " \
                   "JOIN physician ph ON intpr.physician_id = ph.user_id " \
                   "JOIN user u ON ph.user_id = u.user_id " \
                   "JOIN request req ON intpr.request_id = req.request_id " \
                   "JOIN medical_image m ON intpr.image_id = m.image_id " \
                   "JOIN user pa ON pa.user_id = m.user_id " \
                   "WHERE intpr.intpr_id =%s" % intpr_id

        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query)
                self.connector.commit()
                for row in cursor:
                    intpr_detail['intpr_id'] = row[0]
                    intpr_detail['physician_id'] = row[1]
                    intpr_detail['physician_name'] = row[2] + ' ' + row[3]
                    intpr_detail['level'] = row[4]
                    intpr_detail['summary'] = row[5]
                    intpr_detail['suspected_disease'] = row[6]
                    intpr_detail['opinion'] = row[7]
                    intpr_detail['recommendation'] = row[8]
                    intpr_detail['image_subject'] = row[9]
                    intpr_detail['image_type'] = row[10]
                    intpr_detail['image_date'] = row[11]
                    intpr_detail['medical_department'] = row[12]
                    intpr_detail['taken_from'] = row[13]
                    intpr_detail['physician'] = row[14]
                    intpr_detail['place'] = row[15]
                    intpr_detail['description'] = row[16]
                    intpr_detail['request_subject'] = row[17]
                    intpr_detail['request_message'] = row[18]
                    intpr_detail['image_id'] = row[19]
                    intpr_detail['patient_id'] = row[20]
                    intpr_detail['name'] = row[21]
                    intpr_detail['email'] = row[22]
                    intpr_detail['phone_number'] = row[23]
            except Exception as e:
                logger.exception(e)
                raise Exception("retrieve_physician_interpretation_detail Error" + e.message)

        return intpr_detail

    # KH's
    def retrieve_patient_intpr_list(self, patient_id, time_from=None):
        intprs = []
        time_from = int(time_from) if time_from is not None else 0
        db_query = "SELECT intpr.intpr_id, req.timestamp, intpr.timestamp, req.subject, " \
                   "m.image_type, req.level, intpr.summary, " \
                   "intpr.suspected_disease, intpr.opinion, intpr.recommendation, " \
                   "req.subject, m.subject " \
                   "FROM interpretation intpr " \
                   "JOIN request req ON intpr.request_id = req.request_id " \
                   "JOIN medical_image m ON intpr.image_id = m.image_id " \
                   "WHERE intpr.patient_id='%s' and intpr.timestamp>%s " \
                   "ORDER BY intpr.timestamp DESC" % (patient_id, time_from)
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
                    intpr['suspected_disease'] = row[7]
                    intpr['opinion'] = row[8]
                    intpr['recommendation'] = row[9]
                    intpr['request_subject'] = row[10]
                    intpr['image_subject'] = row[11]
                    intprs.append(intpr)
            except Exception as e:
                logger.exception(e)
                raise Exception("retrieve_patient_intpr_list Error" + e.message)
        return intprs

    # KH
    def retrieve_physician_intpr_list(self, physician_id, time_from=None):
        intprs = []
        time_from = int(time_from) if time_from is not None else 0
        db_query = "SELECT intpr.intpr_id, req.timestamp, intpr.timestamp, req.subject, " \
                   "m.image_type, req.level, intpr.summary, " \
                   "intpr.suspected_disease, intpr.opinion, intpr.recommendation, " \
                   "m.user_id, m.subject " \
                   "FROM interpretation intpr " \
                   "JOIN request req ON intpr.request_id = req.request_id " \
                   "JOIN medical_image m ON intpr.image_id = m.image_id " \
                   "WHERE intpr.physician_id='%s' and intpr.timestamp>%s " \
                   "ORDER BY intpr.timestamp DESC" % (physician_id, time_from)

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
                    intpr['suspected_disease'] = row[7]
                    intpr['opinion'] = row[8]
                    intpr['recommendation'] = row[9]
                    intpr['patient_id'] = row[10]
                    intpr['image_subject'] = row[11]
                    intprs.append(intpr)
            except Exception as e:
                logger.exception(e)
                raise Exception("retrieve_physician_intpr_list Error" + e.message)
        return intprs

    # HT for redirection
    def retrieve_interpretation_by_request_id(self, request_id):
        db_query = "SELECT intpr_id FROM interpretation WHERE request_id=%s"
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(db_query, request_id)
                for row in cursor:
                    return row[0]
            except Exception as e:
                return None
        return None

    ### Session
    def add_session(self, *args):
        """
        :param args: patient_id, physician_id, type, value, timestamp
                value: a json string
        :return: boolean
        """
        with self.connector.cursor() as cursor:
            try:
                db_query = "INSERT INTO session (patient_id, physician_id, type, value, timestamp) " \
                           "VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(db_query, args)
                self.connector.commit()

                if cursor.rowcount:
                    return True
                else:
                    return False
            except Exception as e:
                logger.exception(e)
                return False

    def retrieve_patient_session(self, user_id):
        result = []
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT s.*, phi.first_name, phi.last_name " \
                           "FROM session s " \
                           "JOIN physician_info phi ON s.physician_id = phi.user_id " \
                           "WHERE patient_id = %s and status < 2 " \
                           "ORDER BY s.status asc, s.timestamp desc;"
                cursor.execute(db_query, user_id)
                for row in cursor:
                    session = {}
                    session['session_id'] = row[0]
                    session['patient_id'] = row[1]
                    session['physician_id'] = row[2]
                    session['type'] = row[3]
                    session['value'] = json.loads(row[4])
                    session['timestamp'] = row[5]
                    session['status'] = row[6]
                    session['first_name'] = row[7]
                    session['last_name'] = row[8]
                    session['name'] = row[7] + ' ' + row[8]
                    result.append(session)
            except Exception as e:
                logger.exception(e)
                raise Exception("Unknown error occurs in session retrieval.")
        return result

    def retrieve_physician_session(self, user_id):
        result = []
        with self.connector.cursor() as cursor:
            try:
                db_query = "SELECT s.*, pai.first_name, pai.last_name " \
                           "FROM session s " \
                           "JOIN patient_info pai ON s.patient_id = pai.user_id " \
                           "WHERE physician_id = %s and status < 2 " \
                           "ORDER BY s.status asc, s.timestamp desc;"
                cursor.execute(db_query, user_id)
                for row in cursor:
                    session = {}
                    session['session_id'] = row[0]
                    session['patient_id'] = row[1]
                    session['physician_id'] = row[2]
                    session['type'] = row[3]
                    session['value'] = json.loads(row[4])
                    session['timestamp'] = row[5]
                    session['status'] = row[6]
                    session['first_name'] = row[7]
                    session['last_name'] = row[8]
                    session['name'] = row[7] + ' ' + row[8]
                    result.append(session)
            except Exception as e:
                logger.exception(e)
                raise Exception("Unknown error occurs in session retrieval.")
        return result

    def update_session(self, session_id):
        with self.connector.cursor() as cursor:
            try:
                db_query = "UPDATE session SET status = 1 " \
                           "WHERE session_id = %s"
                cursor.execute(db_query, session_id)
                self.connector.commit()
            except Exception as e:
                logger.exception(e)
                return False
        return True

    def delete_session(self, session_id):
        with self.connector.cursor() as cursor:
            try:
                db_query = "UPDATE session SET status = 2 " \
                           "WHERE session_id = %s"
                cursor.execute(db_query, session_id)
                self.connector.commit()

            except Exception as e:
                logger.exception(e)
                return False
        return True

    def close(self):
        self.connector.close()
