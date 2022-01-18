"""
Date: 2020.04.22
Programmer: DY
Description: Code for CRUD with images
"""
import os
import shutil

import pymysql
import constants


class Image:
    def __init__(self):
        self.db = DBImages()
        self.img_path = None

    def register_images(self, uploader_id, img_type, img_path, acq_date, first_name, last_name, birthday, gender,
                        examination_source, interpretation, description, medical_record_number):
        result = self.db.register_images(uploader_id, img_type, img_path, acq_date, first_name, last_name, birthday, gender,
                        examination_source, interpretation, description, medical_record_number)
        return result

    def retrieve_images(self, uploader_id=None, img_id=None, img_path=None):
        result = self.db.retrieve_images(uploader_id=uploader_id, img_id=img_id,
                                         img_path=img_path)
        return result

    def modify_images(self, img_id, img_path=None, img_datetime=None):
        result = self.db.modify_images(imag_id=img_id, img_path=img_path,
                                       img_datetime=img_datetime)
        return result

    def delete_images(self, img_id):
        try:
            # To need to change the part of showing data
            data = self.db.retrieve_images(img_id=img_id)
            print(img_id, data[0]["img_path"])
            shutil.rmtree(data[0]["img_path"])

            result = os.path.exists(data[0]["img_path"])
            if not result:  # when folder is removed
                result = self.db.delete_images(img_id=img_id)
                return result
            return False
        except:
            return False


class DBImages:
    def __init__(self):
        """
        To define db connection
        """
        try:
            self.conn = pymysql.connect(host=constants.HOST_ADDR, user='root', password='root', db='mias',
                                        charset='utf8', autocommit=True, cursorclass=pymysql.cursors.DictCursor)
        except Exception as e:
            self.conn = None

    def register_images(self, uploader_id, img_type, img_path, acq_date, first_name, last_name, birthday, gender,
                        examination_source, interpretation, description, medical_record_number):
        sql = "INSERT INTO images (uploader_id, img_type, img_path, acquisition_date," \
              " first_name, last_name, birthday, gender, examination_source, interpretation, description, medical_record_number)" \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (uploader_id, str(img_type), str(img_path), str(acq_date), str(first_name),
                                     str(last_name), str(birthday), str(gender), str(examination_source), str(interpretation),
                                     str(description), str(medical_record_number)))
            self.conn.commit()
            return True
        except:
            return False

    def retrieve_images(self, uploader_id=None, img_id=None, img_path=None):
        sql = "SELECT * FROM images"
        if any([uploader_id, img_id, img_path]):  # if more than one inputs are not none, any() returns true
            sql += " WHERE "
        if uploader_id is not None:
            sql += "uploader_id=" + str(uploader_id)
            if any([img_id, img_path]):
                sql += " AND "
        if img_id is not None:
            sql += "img_id=" + str(img_id)
            if any([img_path]):
                sql += " AND "
        if img_path is not None:
            sql += "img_path='" + img_path + "'"

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        except:
            return []

    def modify_images(self, imag_id, img_path=None, img_datetime=None):
        sql = "UPDATE images SET "
        if img_path is not None:
            sql += "img_path" + img_path + "'"
            if any([]):
                sql += ", "
        if img_datetime is not None:
            sql += "img_datetime'" + img_datetime + "'"

        sql += " WHERE imgae_id=" + str(imag_id)

    def delete_images(self, img_id):
        try:
            with self.conn.cursor() as cursor:
                sql = "delete from images where img_id=%s"
                cursor.execute(sql, img_id)
                self.conn.commit()
                return True
        except:
            return False


if __name__ == '__main__':
    img = Image()

    # register
    # print(img.register_images(uploader_id=1, img_path='E:\dataset', img_datetime='2020.04.22'))

    # retrieve
    print(img.retrieve_images(uploader_id=1))