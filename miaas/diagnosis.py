"""
Date: 2022. 01. 06.
Programmer: MH
Description: Code for diagnosis
"""
import datetime
import os
import shutil

import pymysql
import constants
from datetime import datetime

class Diagnosis:
    def __init__(self):
        self.db = DBDiagnosis()

    def register_diagnosis(self, pat_name, mrn, birthday, img_id, tumor_types, aphe_types, tumor_sizes, num_mfs, stages):
        diagnosis_date = datetime.today().strftime("%m-%d-%Y")
        result = self.db.register_diagnosis(pat_name, mrn, birthday, img_id, tumor_types, aphe_types, tumor_sizes, num_mfs, stages, diagnosis_date)
        return result

    def retrieve_diagnosis(self, diagnosis_id=None):
        result = self.db.retrieve_diagnosis(diagnosis_id)
        return result

class DBDiagnosis:
    def __init__(self):
        """
        To define db connection
        """
        try:
            self.conn = pymysql.connect(host=constants.HOST_ADDR, user='root', password='root', db='post_enhancement',
                                        charset='utf8', autocommit=True, cursorclass=pymysql.cursors.DictCursor)
        except Exception as e:
            self.conn = None

    def register_diagnosis(self, pat_name, mrn, birthday, img_id, tumor_types, aphe_types, tumor_sizes, num_mfs, stages, diagnosis_date):
        sql = "INSERT INTO diagnosis_liver (pat_name, mrn, birthday, img_id, tumor_types, aphe_types, tumor_sizes, num_mfs, stages, diagnosis_date)" \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (pat_name, mrn, birthday, img_id, tumor_types, aphe_types, tumor_sizes, num_mfs, stages, diagnosis_date))
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def retrieve_diagnosis(self, diagnosis_id=None):
        sql = "SELECT * FROM diagnosis_liver"
        if diagnosis_id is not None:
            sql += " WHERE diagnosis_id="+str(diagnosis_id)

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        except:
            return []

if __name__ == '__main__':
    ds = Diagnosis()
    # print(ds.register_diagnosis("test", "test","test","test", "test","test","test", "test","test"))
    print(ds.retrieve_diagnosis())