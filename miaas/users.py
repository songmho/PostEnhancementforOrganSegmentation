"""
Date: 2019.10.11
Programmer: MH
Description: Code for user class and related classes
"""
import constants
import pymysql


class User:
    """
    class for user
    """

    def __init__(self):
        self.identification_number = None
        self.first_name = None
        self.last_name = None
        self.email = None
        self.phone_number = None
        self.pwd = None
        self.role = None
        self.active = None
        self.db = DBUser()

    def register_user(self, first_name, last_name, email, phone_number, pwd, role, active):
        """
        To register user data
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param email: string, user's email
        :param phone_number: string, user's phone number
        :param pwd: string, user's password
        :param role: string, role of the user. physician, patient, staff.
        :param active: boolean, whether account is activated or not
        :return: boolean, state of registering
        """
        # result is identification_number of user table
        result = self.db.register_user(first_name, last_name, email, phone_number, pwd, role, active)
        if result != 1:
            self.identification_number = result
            self.first_name = first_name
            self.last_name = last_name
            self.email = email
            self.phone_number = phone_number
            self.pwd = pwd
            self.role = role
            self.active = active
        return result

    def retrieve_user(self, identification_number=None, first_name=None, last_name=None, email=None, phone_number=None,
                      pwd=None, role=None, active=None):
        """
        To retrieve user using input information
        :param identification_number: int, user's identification_number
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param email: string, user's email
        :param phone_number: string, user's phone number
        :param pwd: string, user's password
        :param role: string, role of the user. Physician, Patient, Staff.
        :param active: boolean, membership certification
        :return: list, list of found users
        """
        result = self.db.retrieve_user(identification_number=identification_number, first_name=first_name,
                                       last_name=last_name, email=email,
                                       phone_number=phone_number, pwd=pwd, role=role, active=active)
        return result

    def modify_user(self, identification_number, first_name=None, last_name=None, email=None, phone_number=None,
                    pwd=None, role=None, active=None):
        """
        To modify user information
        :param identification_number: int, user's identification_number
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param email: string, user's email
        :param phone_number: string, user's phone number
        :param pwd: string, user's password
        :param role: string, role of the user. physician, patient, staff.
        :param active: boolean, whether account is activated or not
        :return: boolean, state of modifying
        """
        result = self.db.modify_user(identification_number=identification_number, first_name=first_name,
                                     last_name=last_name, email=email,
                                     phone_number=phone_number, pwd=pwd, role=role, active=active)
        if result:
            if first_name is not None:
                self.first_name = first_name
            if last_name is not None:
                self.last_name = last_name
            if email is not None:
                self.email = email
            if phone_number is not None:
                self.phone_number = phone_number
            if pwd is not None:
                self.pwd = pwd
            if role is not None:
                self.role = role
            if active is not None:
                self.active = active
        return result

    def delete_user(self):
        self.db.delete_user(self.identification_number)


class Physician(User):
    """
    Class for evaluator(Physician)
    """

    def __init__(self):
        self.identification_number = None
        self.id = None
        self.first_name = None
        self.last_name = None
        self.email = None
        self.phone_number = None
        self.pwd = None
        self.role = None
        self.active = None
        self.db = DBPhysician()

    def register_physician(self, first_name, last_name, email, phone_number, pwd, role, active):
        print(">>>", role)
        result = self.db.register_physician(first_name, last_name, email, phone_number, pwd, role, active)

        return result

    def retrieve_physician(self, identification_number=None, id=None, first_name=None, last_name=None, email=None,
                           phone_number=None,
                           pwd=None, role=None, active=None):
        result = self.db.retrieve_physician(identification_number=identification_number, id=id, first_name=first_name,
                                            last_name=last_name, email=email,
                                            phone_number=phone_number, pwd=pwd, role=role, active=active)
        return result

    def modify_physician(self, identification_number=None, first_name=None, last_name=None, email=None,
                         phone_number=None,
                         pwd=None, role=None, active=None):
        result = self.db.modify_physician(identification_number=identification_number, first_name=first_name,
                                          last_name=last_name, email=email,
                                          phone_number=phone_number, pwd=pwd, role=role, active=active)
        if result:
            if first_name is not None:
                self.first_name = first_name
            if last_name is not None:
                self.last_name = last_name
            if email is not None:
                self.email = email
            if phone_number is not None:
                self.phone_number = phone_number
            if pwd is not None:
                self.pwd = pwd
            if role is not None:
                self.role = role
            if active is not None:
                self.active = active
        return result

    def delete_physician(self):
        result = self.db.delete_physician(self.identification_number)


class Patient(User):
    """
    Class for trainee
    """

    def __init__(self):
        self.identification_number = None
        self.id = None
        self.first_name = None
        self.last_name = None
        self.email = None
        self.phone_number = None
        self.pwd = None
        self.role = None
        self.active = None
        self.db = DBPatient()

    def register_patient(self, first_name, last_name, email, phone_number, pwd, role, active):
        result = self.db.register_patient(first_name, last_name, email, phone_number, pwd, role, active)

        return result

    def retrieve_patient(self, identification_number=None, id=None, first_name=None, last_name=None, email=None,
                         phone_number=None, pwd=None, role=None, active=None):
        result = self.db.retrieve_patient(identification_number=identification_number, id=id, first_name=first_name,
                                          last_name=last_name, email=email,
                                          phone_number=phone_number, pwd=pwd, role=role, active=active)
        return result

    def modify_patient(self, identification_number=None, first_name=None, last_name=None, email=None,
                       phone_number=None,
                       pwd=None, role=None, active=None):
        result = self.db.modify_patient(identification_number=identification_number, first_name=first_name,
                                        last_name=last_name, email=email,
                                        phone_number=phone_number, pwd=pwd, role=role, active=active)
        if result:
            if first_name is not None:
                self.first_name = first_name
            if last_name is not None:
                self.last_name = last_name
            if email is not None:
                self.email = email
            if phone_number is not None:
                self.phone_number = phone_number
            if pwd is not None:
                self.pwd = pwd
            if role is not None:
                self.role = role
            if active is not None:
                self.active = active
        return result

    def delete_patient(self):
        result = self.db.delete_patient(self.identification_number)


class Staff(User):
    """
    Class for Staff
    """

    def __init__(self):
        self.identification_number = None
        self.id = None
        self.first_name = None
        self.last_name = None
        self.email = None
        self.phone_number = None
        self.pwd = None
        self.role = None
        self.active = None
        self.db = DBStaff()

    def register_staff(self, first_name, last_name, email, phone_number, pwd, role, active):
        result = self.db.register_staff(first_name, last_name, email, phone_number, pwd, role, active)

        return result

    def retrieve_staff(self, identification_number=None, id=None, first_name=None, last_name=None, email=None,
                       phone_number=None,
                       pwd=None, role=None, active=None):
        result = self.db.retrieve_staff(identification_number=identification_number, id=id, first_name=first_name,
                                        last_name=last_name, email=email,
                                        phone_number=phone_number, pwd=pwd, role=role, active=active)
        return result

    def modify_staff(self, identification_number=None, first_name=None, last_name=None, email=None,
                     phone_number=None,
                     pwd=None, role=None, active=None):
        result = self.db.modify_staff(identification_number=identification_number, first_name=first_name,
                                      last_name=last_name, email=email,
                                      phone_number=phone_number, pwd=pwd, role=role, active=active)
        if result:
            if first_name is not None:
                self.first_name = first_name
            if last_name is not None:
                self.last_name = last_name
            if email is not None:
                self.email = email
            if phone_number is not None:
                self.phone_number = phone_number
            if pwd is not None:
                self.pwd = pwd
            if role is not None:
                self.role = role
            if active is not None:
                self.active = active
        return result

    def delete_staff(self):
        result = self.db.delete_staff(self.identification_number)


class DBUser:
    """
    class for user table
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

    def register_user(self, first_name, last_name, email, phone_number, pwd, role, active):
        """
        To register user data
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param email: string, user's email
        :param phone_number: string, user's phone number
        :param pwd: string, user's password
        :param role: string, role of the user. physician, patient, staff.
        :param active: boolean, whether account is activated or not
        :return: boolean, state of registering
        """
        sql = "INSERT INTO users (first_name, last_name, email, phone_number, pwd, role, active)" \
              "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        already_regist = self.retrieve_user(email=email)
        if len(already_regist) > 0:
            return False
        else:
            try:
                with self.conn.cursor() as cursor:
                    cursor.execute(sql, (str(first_name), str(last_name), str(email),
                                         str(phone_number), str(pwd), str(role), active))
                self.conn.commit()
                return True
            except:
                return False

    def retrieve_user(self, identification_number=None, first_name=None, last_name=None, email=None,
                      phone_number=None, pwd=None, role=None, active=None):
        """
        To retrieve users about input data
        :param identification_number: int, user's identification_number
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param email: string, user's email
        :param phone_number: string, user's phone number
        :param pwd: string, user's password
        :param role: string, role of the user. Physician, Patient, Staff.
        :param active: boolean, membership certification
        :return: list, list of found users
        """
        sql = "SELECT * FROM users"
        if any([identification_number, first_name, last_name, email, phone_number,
                pwd, role, active]):  # if more than one inputs are not none, any() returns true
            sql += " WHERE "
        if identification_number is not None:
            sql += "identification_number=" + str(identification_number)
            if any([first_name, last_name, email, phone_number, pwd, role, active]):
                sql += " AND "
        if first_name is not None:
            sql += "first_name='" + str(first_name) + "'"
            if any([last_name, email, phone_number, pwd, role, active]):
                sql += " AND "
        if last_name is not None:
            sql += "last_name='" + str(last_name) + "'"
            if any([email, phone_number, pwd, role, active]):
                sql += " AND "
        if email is not None:
            sql += "email='" + str(email) + "'"
            if any([phone_number, pwd, role, active]):
                sql += " AND "
        if phone_number is not None:
            sql += "phone_number='" + str(phone_number) + "'"
            if any([pwd, role, active]):
                sql += " AND "
        if pwd is not None:
            sql += "pwd='" + str(pwd) + "'"
            if any([role, active]):
                sql += " AND "
        if role is not None:
            sql += "role='" + str(role) + "'"
            if any([active]):
                sql += " AND "
        if active is not None:
            sql += "active=" + str(active) + ""

        try:
            with self.conn.cursor() as cursor:
                print(sql)
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        except:
            return []

    def modify_user(self, identification_number, first_name=None, last_name=None, email=None, phone_number=None,
                    pwd=None, role=None, active=None):
        """
        To modify user information about input data
        :param identification_number: int, user's identification_number
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param email: string, user's email
        :param phone_number: string, user's phone number
        :param pwd: string, user's password
        :param role: string, role of the user. Physician, Patient, Staff.
        :param active: boolean, whether account is activated or not
        :return: 'True' if successful, or 'False'.
        """
        sql = "UPDATE users SET "
        if first_name is not None:
            sql += "first_name='" + first_name + "'"
            if any([last_name, email, phone_number, pwd, role, active]):
                sql += ", "
        if last_name is not None:
            sql += "last_name='" + last_name + "'"
            if any([email, phone_number, pwd, role, active]):
                sql += ", "
        if email is not None:
            sql += "email='" + email + "'"
            if any([phone_number, pwd, role, active]):
                sql += ", "
        if phone_number is not None:
            sql += "phone_number='" + phone_number + "'"
            if any([pwd, role, active]):
                sql += ", "
        if pwd is not None:
            sql += "pwd='" + pwd + "'"
            if any([role, active]):
                sql += ", "
        if role is not None:
            sql += "role='" + role + "'"
            if any([active]):
                sql += ", "
        if active is not None:
            sql += "active=" + str(active) + ""

        sql += " WHERE identification_number=" + str(identification_number)

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                self.conn.commit()
                return True
        except:
            return False

    def delete_user(self, identification_number):
        """
        To delete course
        :param identification_number: int, user's identification_number (identification number)
        :return: boolean, state of delete
        """
        try:
            with self.conn.cursor() as cursor:
                sql = "delete from users where identification_number=%s"
                cursor.execute(sql, identification_number)
                self.conn.commit()
                return True
        except:
            return False


class DBPhysician(DBUser):
    """
    Class for evaluator
    it inherits User class
    """

    def __init__(self):
        super().__init__()

    def register_physician(self, first_name, last_name, email, phone_number, pwd, role, active):
        """
        To register evaluator with user's information
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param identification_form: string, user's identification form
        :param email: string, user's email
        :param affiliation: string, user's affiliation
        :param phone_number: string, user's phone number
        :param qualification: string, the evaluator's qualification
        :param evaluation_history: string, the evaluator's evolution history
        :param rank: string, the evaluator's rank
        :param department: string, evaluator's department
        :param work_phone: string, evaluator's phone number in work place
        :param work_email: string, evaluator's email in work place
        :return: boolean, state of registration
        """
        result = super().retrieve_user(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number, pwd=pwd, role=role)
        print(result)
        identification_number = result[0]["identification_number"]
        sql = "INSERT INTO physician (identification_number) " \
              "VALUES (%s)"

        # try:
        with self.conn.cursor() as cursor:
            cursor.execute(sql, identification_number)
        self.conn.commit()
        return True
        # except:
        #     return False

    def retrieve_physician(self, identification_number=None, id=None, first_name=None, last_name=None, email=None,
                           phone_number=None, pwd=None, role=None, active=None):
        """
        To retrieve evaluator with user's information
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param identification_form: string, user's identification form
        :param email: string, user's email
        :param affiliation: string, user's affiliation
        :param phone_number: string, user's phone number
        :param qualification: string, the evaluator's qualification
        :param evaluation_history: string, the evaluator's evolution history
        :param rank: string, the evaluator's rank
        :param department: string, evaluator's department
        :param work_phone: string, evaluator's phone number in work place
        :param work_email: string, evaluator's email in work place
        :return: list, evaluator's list
        """
        sql = "SELECT usr.identification_number, identification_number, first_name, last_name, email, phone_number, pwd, role, active" \
              " FROM users as usr INNER JOIN physician as phy ON usr.identification_number=phy.identification_number"

        if any([identification_number, id, first_name, last_name, email, phone_number, pwd, role, active]):
            sql += " WHERE "

        if identification_number is not None:
            sql += "usr.identification_number=" + str(identification_number) + ""
            if any([id, first_name, last_name, email, phone_number, pwd, role, active]):
                sql += " AND "

        if id is not None:
            sql += "phy.id=" + str(id) + ""
            if any([first_name, last_name, email, phone_number, pwd, role, active]):
                sql += " AND "

        if first_name is not None:
            sql += "usr.first_name='" + first_name + "'"
            if any([last_name, email, phone_number, pwd, role, active]):
                sql += " AND "

        if last_name is not None:
            sql += "usr.last_name='" + last_name + "'"
            if any([email, phone_number, pwd, role, active]):
                sql += " AND "

        if email is not None:
            sql += "usr.email='" + email + "'"
            if any([phone_number, pwd, role, active]):
                sql += " AND "
        if phone_number is not None:
            sql += "usr.phone_number='" + phone_number + "'"
            if any([pwd, role, active]):
                sql += " AND "

        if pwd is not None:
            sql += "usr.pwd='" + pwd + "'"
            if any([role, active]):
                sql += " AND "

        if role is not None:
            sql += "usr.role='" + role + "'"
            if any([active]):
                sql += " AND "

        if active is not None:
            sql += "usr.active=" + str(active) + ""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
            return result
        except:
            return []

    def modify_physician(self, identification_number=None, first_name=None, last_name=None, email=None,
                         phone_number=None,
                         pwd=None, role=None, active=None):
        """
        To modify evaluator with user's information
        :param identification_number: int, identification number
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param identification_form: string, user's identification form
        :param email: string, user's email
        :param affiliation: string, user's affiliation
        :param phone_number: string, user's phone number
        :param qualification: string, the evaluator's qualification
        :param evaluation_history: string, the evaluator's evolution history
        :param rank: string, the evaluator's rank
        :param department: string, evaluator's department
        :param work_phone: string, evaluator's phone number in work place
        :param work_email: string, evaluator's email in work place
        :return: boolean, state of modification
        """
        try:
            return super().modify_user(identification_number, first_name, last_name, email, phone_number, pwd, role,
                                       active)
        except:
            return False

    def delete_physician(self, identification_number):
        """
        To delete evaluator
        :param identification_number: int, identification number
        """
        result = False
        try:
            with self.conn.cursor() as cursor:
                sql = "delete from physician where identification_number=%s"
                cursor.execute(sql, identification_number)
                self.conn.commit()
                result = super().delete_user(identification_number)
                return result
        except:
            return result


class DBPatient(DBUser):
    """
    Class for trainee
    it inherits User class
    """

    def __init__(self):
        super().__init__()

    def register_patient(self, first_name, last_name, email, phone_number, pwd, role, active):
        """
        To register trainee information
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param identification_form: string, user's identification form
        :param email: string, user's email
        :param affiliation: string, user's affiliation
        :param phone_number: string, user's phone number
        :param qualification: string, the evaluator's qualification
        :param rank: string, the evaluator's rank
        :param department: string, evaluator's department
        :param work_phone: string, evaluator's phone number in work place
        :param work_email: string, evaluator's email in work place
        :return: Boolean, state of registration
        """
        result = super().retrieve_user(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number, pwd=pwd, role=role)
        print(result)
        identification_number = result[0]["identification_number"]
        sql = "INSERT INTO patient (identification_number) " \
              "VALUES (%s)"

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, identification_number)
            self.conn.commit()
            return True
        except:
            return False

    def retrieve_patient(self, identification_number=None, id=None, first_name=None, last_name=None, email=None,
                         phone_number=None, pwd=None, role=None, active=None):
        """
        to retrieve trainee following input data
        :param identification_number: int, identification number
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param identification_form: string, user's identification form
        :param email: string, user's email
        :param affiliation: string, user's affiliation
        :param phone_number: string, user's phone number
        :param qualification: string, the evaluator's qualification
        :param rank: string, the evaluator's rank
        :param department: string, evaluator's department
        :param work_phone: string, evaluator's phone number in work place
        :param work_email: string, evaluator's email in work place
        :return: list, list of found trainee
        """
        sql = "SELECT usr.identification_number, identification_number, first_name, last_name, email, phone_number, pwd, role, active" \
              " FROM users as usr INNER JOIN patient as pat ON usr.identification_number=pat.identification_number"

        if any([identification_number, id, first_name, last_name, email, phone_number, pwd, role, active]):
            sql += " WHERE "

        if identification_number is not None:
            sql += "usr.identification_number=" + str(identification_number) + ""
            if any([id, first_name, last_name, email, phone_number, pwd, role, active]):
                sql += " AND "

        if id is not None:
            sql += "pat.id=" + str(id) + ""
            if any([first_name, last_name, email, phone_number, pwd, role, active]):
                sql += " AND "

        if first_name is not None:
            sql += "usr.first_name='" + first_name + "'"
            if any([last_name, email, phone_number, pwd, role, active]):
                sql += " AND "

        if last_name is not None:
            sql += "usr.last_name='" + last_name + "'"
            if any([email, phone_number, pwd, role, active]):
                sql += " AND "

        if email is not None:
            sql += "usr.email='" + email + "'"
            if any([phone_number, pwd, role, active]):
                sql += " AND "
        if phone_number is not None:
            sql += "usr.phone_number='" + phone_number + "'"
            if any([pwd, role, active]):
                sql += " AND "

        if pwd is not None:
            sql += "usr.pwd='" + pwd + "'"
            if any([role, active]):
                sql += " AND "

        if role is not None:
            sql += "usr.role='" + role + "'"
            if any([active]):
                sql += " AND "

        if active is not None:
            sql += "usr.active=" + str(active) + ""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
            return result
        except:
            return []

    def modify_patient(self, identification_number=None, first_name=None, last_name=None, email=None,
                       phone_number=None,
                       pwd=None, role=None, active=None):
        """
        To modify a trainee following input information
        :param identification_number: int, identification number
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param identification_form: string, user's identification form
        :param email: string, user's email
        :param affiliation: string, user's affiliation
        :param phone_number: string, user's phone number
        :param qualification: string, the evaluator's qualification
        :param rank: string, the evaluator's rank
        :param department: string, evaluator's department
        :param work_phone: string, evaluator's phone number in work place
        :param work_email: string, evaluator's email in work place
        :return: Boolean, state of modification
        """
        try:
            return super().modify_user(identification_number, first_name, last_name, email, phone_number, pwd, role,
                                       active)
        except:
            return False

    def delete_patient(self, identification_number):
        """
        To delete evaluator
        :param identification_number: int, identification number
        :return: boolean, state of deleting trainee
        """
        result = False
        try:
            with self.conn.cursor() as cursor:
                sql = "delete from patient where identification_number=%s"
                cursor.execute(sql, identification_number)
                self.conn.commit()
                result = super().delete_user(identification_number)
                return result
        except:
            return result


class DBStaff(DBUser):
    def __init__(self):
        super().__init__()

    def register_staff(self, first_name, last_name, email, phone_number, pwd, role, active):
        """
        To save new staff information in db
        :param first_name:
        :param last_name:
        :param identification_form:
        :param email:
        :param affiliation:
        :param phone_number:
        :param leader_role:
        :param rank:
        :param department:
        :param work_phone:
        :param work_email:
        :return:
        """

        result = super().retrieve_user(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number, pwd=pwd, role=role)
        print(result)
        identification_number = result[0]["identification_number"]
        sql = "INSERT INTO staff (identification_number) " \
              "VALUES (%s)"

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, identification_number)
            self.conn.commit()
            return True
        except:
            return False

    def retrieve_staff(self, identification_number=None, id=None, first_name=None, last_name=None, email=None,
                       phone_number=None, pwd=None, role=None, active=None):
        """
        To retrieve staff information
        :return:
        """
        sql = "SELECT usr.identification_number, identification_number, first_name, last_name, email, phone_number, pwd, role, active" \
              " FROM users as usr INNER JOIN staff as stf ON usr.identification_number=stf.identification_number"

        if any([identification_number, id, first_name, last_name, email, phone_number, pwd, role, active]):
            sql += " WHERE "

        if identification_number is not None:
            sql += "usr.identification_number=" + str(identification_number) + ""
            if any([id, first_name, last_name, email, phone_number, pwd, role, active]):
                sql += " AND "

        if id is not None:
            sql += "stf.id=" + str(id) + ""
            if any([first_name, last_name, email, phone_number, pwd, role, active]):
                sql += " AND "

        if first_name is not None:
            sql += "usr.first_name='" + first_name + "'"
            if any([last_name, email, phone_number, pwd, role, active]):
                sql += " AND "

        if last_name is not None:
            sql += "usr.last_name='" + last_name + "'"
            if any([email, phone_number, pwd, role, active]):
                sql += " AND "

        if email is not None:
            sql += "usr.email='" + email + "'"
            if any([phone_number, pwd, role, active]):
                sql += " AND "
        if phone_number is not None:
            sql += "usr.phone_number='" + phone_number + "'"
            if any([pwd, role, active]):
                sql += " AND "

        if pwd is not None:
            sql += "usr.pwd='" + pwd + "'"
            if any([role, active]):
                sql += " AND "

        if role is not None:
            sql += "usr.role='" + role + "'"
            if any([active]):
                sql += " AND "

        if active is not None:
            sql += "usr.active=" + str(active) + ""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
            return result
        except:
            return []

    def modify_staff(self, identification_number=None, first_name=None, last_name=None, email=None,
                     phone_number=None,
                     pwd=None, role=None, active=None):
        """
        To modify saved staff information
        :param id:
        :param first_name:
        :param last_name:
        :param identification_form:
        :param email:
        :param affiliation:
        :param phone_number:
        :param leader_role:
        :param rank:
        :param department:
        :param work_phone:
        :param work_email:
        :return:
        """
        try:
            return super().modify_user(identification_number, first_name, last_name, email, phone_number, pwd, role,
                                       active)
        except:
            return False

    def delete_staff(self, identification_number):
        """
        To delete staff information
        :param identification_number: identification number
        :return: boolean, state of deleting the user
        """
        result = False
        try:
            with self.conn.cursor() as cursor:
                sql = "delete from staff where identification_number=%s"
                cursor.execute(sql, identification_number)
                self.conn.commit()
                result = super().delete_user(identification_number)
                return result
        except:
            return result


if __name__ == '__main__':
    usr = User()
    db_usr = DBUser()   # User Test
    # # Register
    # print("ID:", usr.register_user('dy', 'Jeon', 'te2s323st@gmail.com', '010', '0000', 'ghost', 1))
    # retrieve
    # print(usr.retrieve_user(last_name='Jeon'))
    # # modify
    # print("Success?", usr.modify_user(identification_number=4, first_name="DoYeong"))
    # # delete
    # print(usr.delete_user())

    phy = Physician()   # Patient Test
    # db_phy = DBPhysician()
    # Register
    # print("ID:", phy.register_physician('dy', 'Jeon', '0001@gmail.com', '010', '0000', 'ghost', 1))
    # Retrieve
    # print(phy.retrieve_physician(last_name="Jeon", first_name="DoYeong"))
    # modify
    # print("Success?", phy.modify_physician(identification_number=4, role="Human"))
    # Delete
    # print(db_phy.delete_physician(4))

    pat = Patient() # Patient Test
    # Register
    print(pat.register_patient('dy', 'Jeon', '1000@gmail.com', '010', '0000', 'ghost', 1))

    # Retrieve

    # Modify

    # Delete

    # Staff Test
