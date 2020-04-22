"""
Date: 2020.04.22
Programmer: DY
Description: Code for CRUD with images
"""
import pymysql
import constants

class Images:
    def __init__(self):
        self.db = DBImages()
        self.img_path = None

    def register_images(self, uploader_id, img_path, img_datetime):
        result = self.db.register_images(uploader_id, img_path, img_datetime)
        return result

    def retrieve_images(self, uploader_id=None, img_id=None, img_path=None, img_datetime=None):
        result = self.db.retrieve_images(uploader_id=uploader_id, img_id=img_id,
                                         img_path=img_path, img_datetime=img_datetime)
        return result

    def modify_images(self, imag_id, img_path=None, img_datetime=None):
        result = self.db.modify_images(imag_id=imag_id, img_path=img_path,
                                       img_datetime=img_datetime)
        return result

    def delete_images(self, imag_id):
        self.db.delete_images(imag_id=imag_id)


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

    def register_images(self, uploader_id, dicom_img_path, img_datetime):
        sql = "INSERT INTO images (uploader_id, img_path, img_datetime)" \
              "VALUES (%s, %s, %s)"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (str(uploader_id), str(dicom_img_path), str(img_datetime)))
        self.conn.commit()
        is_register = True

        if is_register:
            return self.retrieve_images()[0]["uploader_id"]
        else:
            return -1

    def retrieve_images(self, uploader_id=None, img_id=None, img_path=None, img_datetime=None):
        sql = "SELECT * FROM images"
        if any([uploader_id, img_id, img_path, img_datetime]):  # if more than one inputs are not none, any() returns true
            sql += " WHERE "
        if uploader_id is not None:
            sql += "uploader_id=" + str(uploader_id)
            if any([img_id, img_path, img_datetime]):
                sql += " AND "
        if img_id is not None:
            sql += "img_id=" + str(img_id)
            if any([img_path, img_datetime]):
                sql += " AND "
        if img_path is not None:
            sql += "img_path='" + img_path + "'"
            if any([img_datetime]):
                sql += " AND "
        if img_datetime is not None:
            sql += "img_datetime='" + img_datetime + "'"

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
    img = Images()

    # register
    # print(img.register_images(uploader_id=1, img_path='E:\dataset', img_datetime='2020.04.22'))

    # retrieve
    print(img.retrieve_images(uploader_id=1))