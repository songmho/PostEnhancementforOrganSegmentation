import logging

import pymysql

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
            self.connector = pymysql.connect(host=host, port=port, user=user, passwd=password, db=dbName,
                                             charset='utf8')
            self.is_connected = True
        except Exception as e:
            logger.exception(e)
            raise Exception("DB Connection Error" + e.message)
            self.is_connected = False

    intpr_columns = ["intpr_id", "patient_id", "physician_id", "fee", "interpret_date",
                     "summary", "request_id", "suspected_disease", "opinion", "recommendation"]
    image_columns = ["image_id", "user_id", "image_subject", "image_type", "taken_from", "physician", "place",
                     "description", "image_dir", "size", "upload_date", "intpr_num", "taken_date", "medical_department"]
    request_columns = ["request_id", "status", "request_subject", "request_message", "request_date", "level"]
    response_colunms = ["physician_id", "response_message", "response_date"]

    retrieve_list_query = {
        "patient_image_list":
            {
                "query": "SELECT timestamp, subject, image_type, taken_date, intpr_num, image_id "
                         "FROM miaas.medical_image "
                         "WHERE user_id = %s;",
                "columns": ["uploaded_date", "image_subject", "image_type", "recorded_date", "intpr_num",
                            "image_id"]},

        "patient_intpr_list":
            {
                "query": "SELECT req.timestamp, intpr.timestamp, req.subject, m.subject, m.image_type, req.level, intpr.intpr_id " \
                         "FROM interpretation intpr " \
                         "JOIN request req ON intpr.request_id = req.request_id " \
                         "JOIN medical_image m ON intpr.image_id = m.image_id " \
                         "WHERE intpr.patient_id= %s " \
                         "ORDER BY intpr.timestamp DESC",
                "columns": ["request_date", "interpret_date", "request_subject", "image_subject",
                            "image_type", "level", "intpr_id"]},

        "patient_request_list":
            {
                "query": "SELECT req.timestamp, req.subject, m.subject, m.image_type, req.level, req.status, req.request_id "
                         "FROM miaas.request req " \
                         "JOIN miaas.medical_image m ON req.image_id = m.image_id " \
                         "WHERE m.user_id=%s and req.status > 0 " \
                         "ORDER BY req.timestamp DESC",
                "columns": ["request_date", "request_subject", "image_subject", "image_type", "level",
                            "status", "request_id"]},

        "physician_search_request_list":
            {
                "query": "SELECT req.timestamp, m.user_id, req.subject, m.subject, m.image_type, req.level, req.request_id  " \
                         "FROM request req " \
                         "JOIN medical_image m on req.image_id = m.image_id " \
                         "WHERE status >= 2 and %s NOT IN(SELECT physician_id FROM response res WHERE req.request_id=res.request_id) " \
                         "ORDER BY req.timestamp DESC",
                "columns": ["request_date", "patient_id", "request_subject", "image_subject", "image_type",
                            "level", "request_id"]},

        "physician_response_list":
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

        "physician_intpr_list":
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

    }

    retrieve_query = {
        "patient_intpr_detail":
            {
                "query": "SELECT u.name, req.level, intpr.intpr_id, intpr.patient_id, intpr.physician_id, intpr.fee, "
                         "intpr.timestamp, intpr.summary, intpr.request_id, intpr.suspected_disease, intpr.opinion, intpr.recommendation, "
                         "m.* "
                         "FROM interpretation intpr "
                         "JOIN user u ON intpr.physician_id = u.user_id "
                         "JOIN request req ON intpr.request_id = req.request_id "
                         "JOIN medical_image m ON intpr.image_id = m.image_id "
                         "WHERE intpr.intpr_id = %s",

                "columns": ["physician_name", "level"] + intpr_columns + image_columns},

        "patient_request_detail":
            {
                "query": "SELECT u.name, req.request_id, req.status, req.subject, req.message, req.timestamp, req.level, "
                         "res.physician_id, res.message, res.timestamp, m.* "
                         "FROM request req "
                         "JOIN response res ON req.request_id = res.request_id "
                         "JOIN medical_image m ON req.image_id = m.image_id "
                         "JOIN user u ON u.user_id = res.physician_id "
                         "WHERE req.request_id = %s;",

                "columns": ["physician_name"] + request_columns + response_colunms + image_columns},

        "patient_image_detail":
            {
                "query": "SELECT * "
                         "FROM medical_image "
                         "WHERE image_id=%s",
                "columns": image_columns},

        "physician_intpr_detail":
            {"query": "SELECT u.name, intpr.intpr_id, intpr.patient_id, intpr.physician_id, intpr.fee, "
                      "intpr.timestamp, intpr.summary, intpr.request_id, intpr.suspected_disease, intpr.opinion, intpr.recommendation, "
                      "req.request_id, req.status, req.subject, req.message, req.timestamp, req.level, "
                      "m.* "
                      "FROM interpretation intpr "
                      "JOIN user u ON intpr.physician_id = u.user_id "
                      "JOIN request req ON intpr.request_id = req.request_id "
                      "JOIN medical_image m ON intpr.image_id = m.image_id "
                      "WHERE intpr.intpr_id = %s",

             "columns": ["patient_name"] + intpr_columns + request_columns + image_columns},

        "physician_request_detail":
            {"query": "SELECT u.name, u.phone_number, u.email, "
                      "req.request_id, req.status, req.subject, req.message, req.timestamp, req.level, m.* "
                      "FROM request req "
                      "JOIN medical_image m ON m.image_id = req.image_id "
                      "JOIN user u ON m.user_id = u.user_id "
                      "WHERE req.request_id = %s",

             "columns": ["patient_name", "patient_phone_number", "patient_email"] + intpr_columns + request_columns + image_columns}
    }

    def retrieve_list(self, query_type, *args):
        result = []
        with self.connector.cursor() as cursor:
            try:
                cursor.execute(self.retrieve_list_query[query_type]['query'], args)
                for rows in cursor:
                    temp = {}
                    for key, r in zip(self.retrieve_list_query[query_type]['columns'], rows):
                        temp[key] = r
                    result.append(temp)

            except Exception as e:
                logger.exception(e)
                raise Exception(query_type + " Error :" + e.message)

        return result
