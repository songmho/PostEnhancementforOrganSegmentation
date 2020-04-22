"""
Date: 2020.04.22
Programmer: DY
Description: Code for CRUD with dicom images
"""
import pymysql
import constants

class DicomImages:
    def __init__(self):
        self.db = DBDicomImages()
        self.dicom_img_path = None

    def register_dicom_images(self, uploader_id, dicom_img_path, dicom_img_datetime):
        result = self.db.register_dicom_images(uploader_id, dicom_img_path, dicom_img_datetime)
        return result

    def retrieve_dicom_images(self,  uploader_id=None, dicom_img_id=None, dicom_img_path=None, dicom_img_datetime=None):
        result = self.db.retrieve_dicom_images(uploader_id=uploader_id, dicom_img_id=dicom_img_id,
                                               dicom_img_path=dicom_img_path, dicom_img_datetime=dicom_img_datetime)
        return result

    def modify_dicom_images(self):
        pass

    def delete_dicom_images(self):
        pass


class DBDicomImages:
    def __init__(self):
        """
                To define db connection
                """
        try:
            self.conn = pymysql.connect(host=constants.HOST_ADDR, user='root', password='root', db='mias',
                                        charset='utf8', autocommit=True, cursorclass=pymysql.cursors.DictCursor)
        except Exception as e:
            self.conn = None

    def register_dicom_images(self, uploader_id, dicom_img_path, dicom_img_datetime):
        sql = "INSERT INTO dicom_images (uploader_id, dicom_img_path, dicom_img_datetime)" \
              "VALUES (%s, %s, %s)"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (str(uploader_id), str(dicom_img_path), str(dicom_img_datetime)))
        self.conn.commit()
        is_register = True

        if is_register:
            return self.retrieve_dicom_images()[0]["uploader_id"]
        else:
            return -1

    def retrieve_dicom_images(self, uploader_id=None, dicom_img_id=None, dicom_img_path=None, dicom_img_datetime=None):
        sql = "SELECT * FROM dicom_images"
        if any([uploader_id, dicom_img_id, dicom_img_path, dicom_img_datetime]):  # if more than one inputs are not none, any() returns true
            sql += " WHERE "
        if uploader_id is not None:
            sql += "uploader_id=" + str(uploader_id)
            if any ([dicom_img_id, dicom_img_path, dicom_img_datetime]):
                sql += " AND "
        if dicom_img_id is not None:
            sql += "dicom_img_id=" + str(dicom_img_id)
            if any([dicom_img_path, dicom_img_datetime]):
                sql += " AND "
        if dicom_img_path is not None:
            sql += "dicom_img_path='" + dicom_img_path + "'"
            if any([dicom_img_datetime]):
                sql += " AND "
        if dicom_img_datetime is not None:
            sql += "dicom_img_datetime='" + dicom_img_datetime + "'"

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        except:
            return []
    def modify_dicom_images(self):
        pass

    def delete_dicom_images(self):
        pass


if __name__ == '__main__':
    dcm_img = DicomImages()

    # register
    # print(dcm_img.register_dicom_images(uploader_id=1, dicom_img_path='E:\dataset', dicom_img_datetime='2020.04.22'))

    # retrieve
    print(dcm_img.retrieve_dicom_images(uploader_id=1))