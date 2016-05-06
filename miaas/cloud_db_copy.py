import logging
from _mysql import DataError, IntegrityError, NotSupportedError, OperationalError, ProgrammingError
from pprint import pprint

import pymysql
import time

logging.basicConfig(
    format="[%(name)s][%(asctime)s] %(message)s",
    handlers=[logging.StreamHandler()],
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class DbManager:
    # TABLE COLUMNS
    INTPR_COLUMNS = ["intpr_id", "patient_id", "physician_id", 'image_id', 'level', "fee", "interpret_date",
                     "summary", "request_id", "suspected_disease", "opinion", "recommendation"]
    INTPR_TEMP_COLUMNS = ["request_id", "summary", "suspected_disease", "opinion", "recommendation"]
    IMAGE_COLUMNS = ["image_id", "patient_id", "image_subject", "image_type", "taken_from", "physician", "place",
                     "description", "image_dir", "size", "upload_date", "intpr_num", "taken_date", "medical_department"]
    REQUEST_COLUMNS = ["request_id", "image_id", "status", "request_subject", "request_message", "request_date",
                       "level"]
    RESPONSE_COLUMNS = ["request_id", "physician_id", "response_message", "response_date"]
    PHYSICIAN_COLUMNS = ['user_id', 'physician_name', 'license_number', 'medicine_field', 'certificate_dir',
                         'phone_number', 'email', 'join_date', 'deactivate_date']
    PATIENT_COLUMNS = ['user_id', 'patient_name', 'gender', 'birthday',
                       'phone_number', 'email', 'join_date', 'deactivate_date']
    PHYSICIAN_PROFILE_COLUMNS = ["profile_id", "user_id", "aboutMe", "specialism", "medicalSchool", "graduate",
                                 "certifications", "memberships", "fieldsOfMedicine", "hiv", "offices", "languages",
                                 "insuranceProgram", "healthPlans", "hospitalPrivileges", "malpractice",
                                 "licenseeActions",
                                 "outOfStateActions", "currentLimits", "hspPrivRestrictions", "hspFRPriv",
                                 "criminalConvictions",
                                 "teaching", "serviceActivity", "publications", "statement"]
    SESSION_COLUMNS = ['session_id', "request_id", "patient_id", "physician_id", "session_type", "timestamp", "status"]

    # RETRIEVE LIST QUERY
    PATIENT_IMAGE_LIST = "patient_image_list"
    PATIENT_INTPR_LIST = "patient_intpr_list"
    PATIENT_REQUEST_LIST = "patient_request_list"
    PHYSICIAN_SEARCH_REQUEST_LIST = "physician_search_request_list"
    PHYSICIAN_RESPONSE_LIST = "physician_response_list"
    PHYSICIAN_INTPR_LIST = "physician_intpr_list"
    REQUEST_RESPONSE_LIST = "request_response_list"
    IMAGE_INTPR_LIST = "image_intpr_list"
    PATIENT_INTPR_SESSION = "patient_intpr_session"
    PHYSICIAN_INTPR_DETAIL = "physician_intpr_detail"

    # RETRIEVE DETAIL QUERY
    PATIENT_INFO_ID = "patient_info_id"
    PATIENT_INFO_ID_PASSWORD = "patient_info_id_password"
    PATIENT_INTPR_DETAIL = "patient_intpr_detail"
    PATIENT_REQUEST_DETAIL = "patient_request_detail"
    PATIENT_IMAGE_DETAIL = "patient_image_detail"
    PATIENT_PROFILE = "patient_profile"

    PHYSICIAN_REQUEST_DETAIL = "physician_request_detail"
    PHYSICIAN_INFO_ID = "physician_info_id"
    PHYSICIAN_INFO_ID_PASSWORD = "physician_info_id_password"
    PHYSICIAN_PROFILE = "physician_profile"
    PHYSICIAN_INTPR_SESSION = "physician_intpr_session"

    # RETRIEVE SINGLE COLUMN QUERY
    USER_TYPE = "user_detail"
    FIND_ID = "find_id"
    FIND_PASSWORD = "find_password"
    FIND_USER = "find_user"

    def __init__(self):
        host = 'rainbowdb.czg2t6iatylv.us-west-2.rds.amazonaws.com'
        user = 'smartylab'
        port = 3306
        password = 'lovejesus'
        dbName = 'miaas'
        try:
            self.connector = pymysql.connect(host=host, port=port, user=user, passwd=password, db=dbName,
                                             charset='utf8')
            self.is_connected = True
        except Exception as e:
            logger.exception(e)
            raise Exception("DB Connection Error" + e.message)
            self.is_connected = False

    RETRIEVE_LIST_QUERY = {
        PATIENT_IMAGE_LIST:
            {
                "query": "SELECT timestamp, subject, image_type, taken_date, intpr_num, image_id "
                         "FROM miaas.medical_image "
                         "WHERE user_id = %s;",
                "columns": ["uploaded_date", "image_subject", "image_type", "recorded_date", "intpr_num",
                            "image_id"],
                "error": {
                    IndexError: "",
                    DataError: "",
                    IntegrityError: "",
                    NotSupportedError: "",
                    OperationalError: "",
                    ProgrammingError: "",
                }
            },

        PATIENT_INTPR_LIST:
            {
                "query": "SELECT req.timestamp, intpr.timestamp, req.subject, m.subject, m.image_type, req.level, intpr.intpr_id " \
                         "FROM interpretation intpr " \
                         "JOIN request req ON intpr.request_id = req.request_id " \
                         "JOIN medical_image m ON intpr.image_id = m.image_id " \
                         "WHERE intpr.patient_id= %s " \
                         "ORDER BY intpr.timestamp DESC",
                "columns": ["request_date", "interpret_date", "request_subject", "image_subject",
                            "image_type", "level", "intpr_id"]},

        PATIENT_REQUEST_LIST:
            {
                "query": "SELECT req.timestamp, req.subject, m.subject, m.image_type, req.level, req.status, req.request_id "
                         "FROM miaas.request req " \
                         "JOIN miaas.medical_image m ON req.image_id = m.image_id " \
                         "WHERE m.user_id=%s and req.status > 0 " \
                         "ORDER BY req.timestamp DESC",
                "columns": ["request_date", "request_subject", "image_subject", "image_type", "level",
                            "status", "request_id"]},

        PHYSICIAN_SEARCH_REQUEST_LIST:
            {
                "query": "SELECT req.timestamp, m.user_id, req.subject, m.subject, m.image_type, req.level, req.request_id  " \
                         "FROM request req " \
                         "JOIN medical_image m on req.image_id = m.image_id " \
                         "WHERE status >= 2 and %s NOT IN(SELECT physician_id FROM response res WHERE req.request_id=res.request_id) " \
                         "ORDER BY req.timestamp DESC",
                "columns": ["request_date", "patient_id", "request_subject", "image_subject", "image_type",
                            "level", "request_id"]},

        PHYSICIAN_RESPONSE_LIST:
            {
                "query": "SELECT  req.timestamp, res.timestamp, m.user_id, req.subject, " \
                         "m.subject, m.image_type, req.level, req.status, req.request_id " \
                         "FROM response res " \
                         "JOIN request req on res.request_id = req.request_id " \
                         "JOIN medical_image m on req.image_id = m.image_id  " \
                         "WHERE res.physician_id = %s and req.status > 0 " \
                         "ORDER BY " \
                         "CASE " \
                         "WHEN req.status = 1 Then 3 " \
                         "WHEN req.status = 2 Then 2 " \
                         "WHEN req.status = 0 Then 0 " \
                         "END DESC",
                "columns": ["request_date", "response_date", "patient_id", "request_subject",
                            "image_subject", "image_type", "level", "status", "request_id"]},

        PHYSICIAN_INTPR_LIST:
            {
                "query": "SELECT req.timestamp, intpr.timestamp, m.user_id, m.subject, " \
                         "m.image_type, req.level, intpr.intpr_id " \
                         "FROM interpretation intpr " \
                         "JOIN request req ON intpr.request_id = req.request_id " \
                         "JOIN medical_image m ON intpr.image_id = m.image_id " \
                         "WHERE intpr.physician_id= %s " \
                         "ORDER BY intpr.timestamp DESC",

                "columns": ["request_date", "interpret_date", "patient_id", "image_subject",
                            "image_type", "level", "intpr_id"]},
        REQUEST_RESPONSE_LIST:
            {
                "query": "SELECT phi.user_id, phi.name, phi.medicine_field, phi.phone_number, phi.email, res.message " \
                         "FROM response res " \
                         "JOIN physician_info phi ON res.physician_id = phi.user_id " \
                         "WHERE res.request_id=%s",

                "columns": ["physician_id", "physician_name", "medical_field", "phone_number", 'email',
                            "response_message"]},
        IMAGE_INTPR_LIST:
            {
                "query": "SELECT intpr.*" \
                         "FROM interpretation intpr " \
                         "WHERE image_id=%s",

                "columns": INTPR_COLUMNS},

        PATIENT_INTPR_SESSION:
            {
                "query": "SELECT * " \
                         "FROM intpr_session s " \
                         "JOIN request req ON s.request_id = req.request_id " \
                         "JOIN physician_info phi ON s.physician_id = phi.user_id " \
                         "WHERE patient_id = %s " \
                         "ORDER BY s.status DESC, s.timestamp DESC",

                "columns": [SESSION_COLUMNS, REQUEST_COLUMNS, PHYSICIAN_COLUMNS]
            },

        PHYSICIAN_INTPR_SESSION:
            {
                "query": "SELECT * " \
                         "FROM intpr_session s " \
                         "JOIN request req ON s.request_id = req.request_id " \
                         "JOIN patient_info pai ON s.patient_id = pai.user_id " \
                         "WHERE physician_id = %s " \
                         "ORDER BY s.status DESC, s.timestamp DESC",

                "columns": [SESSION_COLUMNS, REQUEST_COLUMNS, PATIENT_COLUMNS]
            }
    }

    RETRIEVE_DETAIL_QUERY = {
        PATIENT_INTPR_DETAIL:
            {
                "query": "SELECT intpr.*, phi.*, req.*, m.* "
                         "FROM interpretation intpr "
                         "JOIN physician_info phi ON intpr.physician_id = phi.user_id "
                         "LEFT JOIN request req ON intpr.request_id = req.request_id "
                         "JOIN medical_image m ON intpr.image_id = m.image_id "
                         "WHERE intpr.intpr_id = %s",

                "columns": [INTPR_COLUMNS, PHYSICIAN_COLUMNS + ["password"], REQUEST_COLUMNS, IMAGE_COLUMNS]},

        PATIENT_REQUEST_DETAIL:
            {
                "query": "SELECT req.*, m.*  "
                         "FROM request req "
                         "JOIN medical_image m ON req.image_id = m.image_id "
                         "WHERE req.request_id = %s;",

                "columns": [REQUEST_COLUMNS, IMAGE_COLUMNS]},

        PATIENT_IMAGE_DETAIL:
            {
                "query": "SELECT * "
                         "FROM medical_image "
                         "WHERE image_id=%s",
                "columns": [IMAGE_COLUMNS]},

        PHYSICIAN_REQUEST_DETAIL:
            {"query": "SELECT req.*, pai.*, m.*, intpr_temp.* "
                      "FROM request req "
                      "JOIN medical_image m ON m.image_id = req.image_id "
                      "JOIN patient_info pai ON m.user_id = pai.user_id "
                      "LEFT JOIN interpretation_temp intpr_temp ON req.request_id = intpr_temp.request_id "
                      "WHERE req.request_id = %s",

             "columns": [REQUEST_COLUMNS, PATIENT_COLUMNS + ["password"], IMAGE_COLUMNS, INTPR_TEMP_COLUMNS]},

        PHYSICIAN_INTPR_DETAIL:
            {"query": "SELECT intpr.*, pai.*, req.*, m.* "
                      "FROM interpretation intpr "
                      "JOIN patient_info pai ON intpr.patient_id = pai.user_id "
                      "JOIN request req ON intpr.request_id = req.request_id "
                      "JOIN medical_image m ON intpr.image_id = m.image_id "
                      "WHERE intpr.intpr_id = %s",

             "columns": [INTPR_COLUMNS, PATIENT_COLUMNS + ["password"], REQUEST_COLUMNS, IMAGE_COLUMNS]},
        PATIENT_INFO_ID:
            {"query": "SELECT * "
                      "FROM patient_info "
                      "WHERE user_id = %s",

             "columns": [PATIENT_COLUMNS]},

        PATIENT_INFO_ID_PASSWORD:
            {"query": "SELECT *  "
                      "FROM patient_info "
                      "WHERE user_id = %s and password = %s",

             "columns": [PATIENT_COLUMNS + ["password"]]},

        PHYSICIAN_INFO_ID:
            {"query": "SELECT *  "
                      "FROM physician_info "
                      "WHERE user_id = %s",

             "columns": [PHYSICIAN_COLUMNS]},

        PHYSICIAN_INFO_ID_PASSWORD:
            {"query": "SELECT *  "
                      "FROM patient_info "
                      "WHERE user_id = %s and password = %s",

             "columns": [PHYSICIAN_COLUMNS + ["password"]]},

        PHYSICIAN_PROFILE:
            {"query": "SELECT *  "
                      "FROM physician_profile "
                      "WHERE user_id = %s",

             "columns": [PHYSICIAN_PROFILE_COLUMNS]},

        PATIENT_PROFILE:
            {"query": "SELECT pp.type, pp.value, pp.timestamp " \
                      "From (" \
                      "  SELECT @row_num := IF(@prev_value=p.type, @row_num+1, 1) as rnd, p.*, @prev_value := p.type " \
                      "  From patient_profile p, (select @row_num := 1) x, (select @prev_value := '') y " \
                      "  WHERE p.user_id = %s " \
                      "  ORDER BY p.type, p.timestamp DESC" \
                      ") pp " \
                      "Where pp.rnd = 1"},



    }

    RETRIEVE_SINGLE_COLUMN_QUERY = {
        USER_TYPE:
            {"query": "SELECT user_type "
                      "FROM user "
                      "WHERE user_id = %s and password = %s"},
        FIND_USER:
            {"query": "SELECT IF(count(1), 'True', 'False') "
                      "FROM user "
                      "WHERE user_id = %s"},
        FIND_ID:
            {"query": "SELECT user_id "
                      "FROM user "
                      "WHERE email=%s AND name=%s"},

        FIND_PASSWORD:
            {"query": "SELECT password "
                      "FROM user "
                      "WHERE email=%s AND name=%s"},
    }

    def retrieve_single_column(self, query_type, *args):
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(self.RETRIEVE_SINGLE_COLUMN_QUERY[query_type]['query'], args)
                row = cursor.fetchone()
                if row[0] == "True":
                    return True
                else:
                    return row[0]
            except Exception as e:
                logger.exception(e)
                raise Exception(query_type + " Error :" + e.message)

    def retrieve_list(self, query_type, *args):
        result = []
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(self.RETRIEVE_LIST_QUERY[query_type]['query'], args)
                for rows in cursor:
                    temp = {}
                    for key, r in zip(self.RETRIEVE_LIST_QUERY[query_type]['columns'], rows):
                        temp[key] = r
                    result.append(temp)

            except Exception as e:
                logger.exception(e)
                raise Exception(query_type + " Error :" + e.message)

        return result

    def retrieve_detail(self, query_type, *args):
        result = []
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(self.RETRIEVE_DETAIL_QUERY[query_type]['query'], args)
                if query_type == self.PATIENT_PROFILE:
                    for row in cursor:
                        profile = {}
                        profile['type'] = row[0]
                        profile['value'] = row[1]
                        profile['timestamp'] = row[2]
                        result.append(profile)
                else:
                    row = cursor.fetchone()
                    row_idx = 0
                    for columns in self.RETRIEVE_DETAIL_QUERY[query_type]['columns']:
                        temp = {}
                        for key in columns:
                            temp[key] = row[row_idx]
                            row_idx += 1
                        result.append(temp)
            except Exception as e:
                logger.exception(e)
                raise Exception(query_type + " Error :" + e.message)

        return result

    def add_session(self, *args):
        with self.connector.cursor() as cursor:
            try:
                db_query = "INSERT INTO intpr_session (request_id, patient_id, physician_id, session_type, timestamp)" \
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

    def add_cancel_session(self, *args):
        with self.connector.cursor() as cursor:
            try:
                db_query = "INSERT INTO intpr_session (patient_id, physician_id, session_type, timestamp)" \
                           "VALUES (%s, %s, %s, %s)"
                cursor.execute(db_query, args)
                self.connector.commit()

                if cursor.rowcount:
                    return True
                else:
                    return False
            except Exception as e:
                logger.exception(e)
                return False

    def update_session(self, session_id):
        with self.connector.cursor() as cursor:
            try:
                db_query = "UPDATE intpr_session SET status = 1 " \
                           "WHERE session_id = %s"
                cursor.execute(db_query, session_id)
                self.connector.commit()

                if cursor.rowcount:
                    return True
                else:
                    return False
            except Exception as e:
                logger.exception(e)
                return False

    def delete_session(self, session_id):
        with self.connector.cursor() as cursor:
            try:
                db_query = "DELETE FROM intpr_session " \
                           "WHERE session_id = %s"
                cursor.execute(db_query, session_id)
                self.connector.commit()

                if cursor.rowcount:
                    return True
                else:
                    return False
            except Exception as e:
                logger.exception(e)
                return False


if __name__ == '__main__':
    db = DbManager()
    timestamp = int(round(time.time() * 1000))
    result = db.retrieve_detail(2, 'demopa', 'demoph', 'response', timestamp)
    pprint(result)
