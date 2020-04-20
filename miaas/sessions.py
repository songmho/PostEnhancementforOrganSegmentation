"""
Date: 2020.04.20
Programmer: MH
Description:
"""
import random
import secrets
import string
import time
from datetime import datetime

import pymysql

from miaas import constants


class Session:
    """
    Class for session management
    """
    def __init__(self):
        self.db_session = DBSession()

    def generate_token(self):
        """
        To generate random string
        :return: string, token
        """
        token = ''.join(random.choice(string.ascii_lowercase) for x in range(45))
        return token

    def generate_session(self, u_id):
        """
        To generate session for target user
        :param u_id: int, user id (identification_number )
        :return: boolean, whether session is activated or not
        """
        sessions = self.db_session.retrieve_session(u_id=u_id)
        if len(sessions) > 0:
            last_session = sessions[-1]
            print(type(last_session['start_time']), last_session['start_time'])
            t_tuple = last_session['start_time'].timetuple()
            s_t = time.mktime(t_tuple)
            diff = time.time() - s_t
            if last_session['expired_time'] is None:
                if diff > 10*60:    # 10 min
                    # To expire current session
                    self.expire_session(u_id)
                else:
                    return False
            else:
                pass
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        token = self.generate_token()
        result = self.db_session.create_session(u_id=u_id, t_1=start_time, token=token)
        return result

    def expire_session(self, u_id):
        """
        To expire session for target user
        :param u_id:
        :return: boolean, expired or not
        """
        expired_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result = self.db_session.modify_session(u_id=u_id, t_2=expired_time)

        return result

    def check_session(self, u_id, token):
        """
        To check that current session of current user is available
        :param u_id: user's id
        :param token: user's token
        :return: boolean, available or not
        """
        result = self.db_session.retrieve_session(u_id, token)

        return result

class DBSession:
    """
    Class for table of Session
    :return:
    """
    def __init__(self):
        """
        To define db connection
        """
        try:
            self.conn = pymysql.connect(host=constants.HOST_ADDR, user='root', password='root', db='mias',
                                        charset='utf8', autocommit=True, cursorclass=pymysql.cursors.DictCursor)
        except Exception as e:
            self.conn = None

    def create_session(self, u_id, t_1, token):
        """
        To create session for the user
        :param u_id:
        :param t_1: '%Y-%m-%d %H:%M:%S'
        :param token:
        :return:
        """
        sql = "INSERT INTO sessions (user_id, start_time, token) VALUES (%s, %s, %s)"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (str(u_id), t_1, str(token)))
            self.conn.commit()
            return True
        except:
            return False

    def retrieve_session(self, u_id, token=None):
        """
        To retrieve session of the user
        :param u_id:
        :return:
        """
        sql = "SELECT * FROM sessions where user_id= "+str(u_id)
        if token is not None:
            sql += " and '"+token+"'"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        except:
            return []

    def modify_session(self, u_id, t_1=None, t_2=None):
        """
        To modify session
        :param u_id:
        :param t:
        :return:
        """
        sql = "UPDATE sessions SET "
        if t_1 is not None:
            sql += "start_time="+t_1
            if t_2 is not None:
                sql += " and "
        if t_2 is not None:
            sql += "expired_time='"+t_2+"'"

        sql += " WHERE user_id="+str(u_id)+" ORDER BY id DESC limit 1"
        # try:
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            self.conn.commit()
            return True
        # except:
        #     return False

    def remove_session(self, id, u_id, t_1, t_2, token):
        """
        To remove session
        :param id:
        :param u_id:
        :param t_1:
        :param t_2:
        :param token:
        :return:
        """
        try:
            with self.conn.cursor() as cursor:
                sql = "delete from users where id=%s"
                cursor.execute(sql, id)
                self.conn.commit()
                return True
        except:
            return False


if __name__ == '__main__':
    s = Session()
    print(s.expire_session(u_id=1))