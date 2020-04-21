"""
Date: 2019.10.11
Programmer: MH
Description: Code for user class and related classes
"""
from . import constants
import pymysql


class User:
    """
    class for user
    """
    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.identification_number = None
        self.identification_form = None
        self.email = None
        self.affiliation = None
        self.phone_number = None
        self.pwd = None
        self.role = None
        self.invitation_code = None
        self.db = DBUser()

    def register_user(self, first_name, last_name, identification_form, email, affiliation, phone_number, pwd, role, invitation_code):
        """
        To register user data
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param identification_form: string, user's identification form
        :param email: string, user's email
        :param affiliation: string, user's affiliation
        :param phone_number: string, user's phone number
        :return: boolean, state of registering
        """
        result = self.db.register_user(first_name, last_name, identification_form, email, affiliation, phone_number, pwd, role, invitation_code)
        if result != 1:
            self.first_name = first_name
            self.last_name = last_name
            self.identification_form = identification_form
            self.email = email
            self.affiliation = affiliation
            self.phone_number = phone_number
            self.pwd = pwd
            self.role = role
            self.identification_number = result
            self.invitation_code = invitation_code
        return result

    def retrieve_user(self, first_name=None, last_name=None, email=None, phone_number=None, pwd=None, invitation_code=None):
        """
        To retrieve user using input information
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param identification_form: string, user's identification form
        :param email: string, user's email
        :param affiliation: string, user's affiliation
        :param phone_number: string, user's phone number
        :return: list, list of found users
        """
        result = self.db.retrieve_user(id=None, first_name=first_name, last_name=last_name, phone_number=phone_number,
                                       email=email, pwd=pwd, invitation_code=invitation_code)

        return result

    def modify_user(self, first_name=None, last_name=None, identification_form=None, email=None, affiliation=None, phone_number=None, pwd=None):
        """
        To modify user information
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param identification_form: string, user's identification form
        :param email: string, user's email
        :param affiliation: string, user's affiliation
        :param phone_number: string, user's phone number
        :param pwd: string, password to change
        :return: boolean, state of modifying
        """
        result = self.db.modify_user(self.identification_number, first_name=first_name, last_name=last_name, pwd=pwd,
                            identification_form=identification_form, affiliation=affiliation, email=email,
                            phone_number=phone_number)
        if result:
            if first_name is not None:
                self.first_name = first_name
            if last_name is not None:
                self.last_name = last_name
            if identification_form is not None:
                self.identification_form = identification_form
            if email is not None:
                self.email = email
            if affiliation is not None:
                self.affiliation = affiliation
            if phone_number is not None:
                self.phone_number = phone_number
            if pwd is not None:
                self.pwd = pwd
        return result

    def delete_user(self):
        self.db.delete_user(self.identification_number)


class Physician(User):
    """
    Class for evaluator
    """
    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.identification_form = None
        self.email = None
        self.affiliation = None
        self.phone_number = None
        self.qualification = None
        self.evaluation_history = None
        self.rank = None
        self.department = None
        self.work_phone = None
        self.work_email = None
        self.role = None
        self.db = DBPhysician()

    def register_physician(self, first_name, last_name, identification_form, email, affiliation, phone_number,
                           qualification, evaluation_history, rank, department, work_phone, work_email, pwd, identification_number):
        result = self.db.register_physician(first_name, last_name, identification_form, email, affiliation, phone_number,
                                            qualification, evaluation_history, rank, department, work_phone, work_email, pwd, identification_number)
        if result != -1:
            self.identification_number = result
            self.first_name = first_name
            self.last_name = last_name
            self.identification_form = identification_form
            self.email = email
            self.affiliation = affiliation
            self.phone_number = phone_number
            self.qualification = qualification
            self.evaluation_history = evaluation_history
            self.rank = rank
            self.department = department
            self.work_phone = work_phone
            self.work_email = work_email
        return result

    def retrieve_physician(self, first_name=None, last_name=None, identification_form=None, email=None,
                           affiliation=None, phone_number=None, qualification=None, evaluation_history=None, rank=None,
                           department=None, work_phone=None, work_email=None, pwd=None):
        result = self.db.retrieve_physician(first_name=first_name, last_name=last_name, email=email, rank=rank,
                                            identification_form=identification_form, affiliation=affiliation, pwd=pwd,
                                            phone_number=phone_number, qualification=qualification, department=department,
                                            evaluation_history=evaluation_history, work_phone=work_phone, work_email=work_email)
        return result

    def modify_physician(self, first_name=None, last_name=None, identification_form=None, email=None,
                         affiliation=None, phone_number=None, qualification=None, evaluation_history=None, rank=None,
                         department=None, work_phone=None, work_email=None, pwd=None):
        result = self.db.modify_physician(id=self.identification_number, first_name=first_name, last_name=last_name,
                                          rank=rank, identification_form=identification_form, affiliation=affiliation, email=email,
                                          phone_number=phone_number, qualification=qualification, department=department, pwd=pwd,
                                          evaluation_history=evaluation_history, work_phone=work_phone, work_email=work_email)
        if result:
            if first_name is not None:
                self.first_name = first_name
            if last_name is not None:
                self.last_name = last_name
            if identification_form is not None:
                self.identification_form = identification_form
            if email is not None:
                self.email = email
            if affiliation is not None:
                self.affiliation = affiliation
            if phone_number is not None:
                self.phone_number = phone_number
            if pwd is not None:
                self.pwd = pwd
            if qualification is not None:
                self.qualification = qualification
            if rank is not None:
                self.rank = rank
            if department is not None:
                self.department = department
            if evaluation_history is not None:
                self.evaluation_history = evaluation_history
            if work_phone is not None:
                self.work_phone = work_phone
            if work_email is not None:
                self.work_email = work_email

    def delete_physician(self):
       result = self.db.delete_physician(self.identification_number)


class Patient(User):
    """
    Class for trainee
    """
    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.identification_form = None
        self.email = None
        self.affiliation = None
        self.phone_number = None
        self.qualification = None
        self.rank = None
        self.department = None
        self.work_phone = None
        self.work_email = None
        self.role = None
        self.db = DBPatient()

    def register_patient(self, first_name, last_name, identification_form, email, affiliation, phone_number,
                         qualification, rank, department, work_phone, work_email, pwd, identification_number):
        result = self.db.register_patient(first_name, last_name, identification_form, email, affiliation, phone_number,
                                          qualification, rank, department, work_phone, work_email, pwd, identification_number)
        return result

    def retrieve_patient(self, first_name=None, last_name=None, identification_form=None, email=None, affiliation=None,
                         phone_number=None, qualification=None, rank=None, department=None, work_phone=None,
                         work_email=None, pwd=None, part_trainee_list=None):
        result = self.db.retrieve_patient(first_name=first_name, last_name=last_name, email=email, rank=rank,
                                          identification_form=identification_form, affiliation=affiliation,
                                          phone_number=phone_number, qualification=qualification, department=department,
                                          work_phone=work_phone, work_email=work_email, pwd=pwd, part_trainee_list=part_trainee_list)
        return result

    def modify_patient(self, first_name=None, last_name=None, identification_form=None, email=None, affiliation=None,
                       phone_number=None, qualification=None, rank=None, department=None, work_phone=None, work_email=None,
                       pwd=None):
        result = self.db.modify_patient(id=self.identification_number, first_name=first_name, last_name=last_name,
                                        rank=rank, identification_form=identification_form, affiliation=affiliation, email=email,
                                        phone_number=phone_number, qualification=qualification, department=department, pwd=pwd,
                                        work_phone=work_phone, work_email=work_email)
        if result:
            if first_name is not None:
                self.first_name = first_name
            if last_name is not None:
                self.last_name = last_name
            if identification_form is not None:
                self.identification_form = identification_form
            if email is not None:
                self.email = email
            if affiliation is not None:
                self.affiliation = affiliation
            if phone_number is not None:
                self.phone_number = phone_number
            if pwd is not None:
                self.pwd = pwd
            if rank is not None:
                self.rank = rank
            if qualification is not None:
                self.qualification = qualification
            if department is not None:
                self.department = department
            if work_phone is not None:
                self.work_phone = work_phone
            if work_email is not None:
                self.work_email = work_email

    def delete_patient(self):
        result = self.db.delete_patient(self.identification_number)


class Staff(User):
    """
    Class for Staff
    """
    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.identification_form = None
        self.email = None
        self.affiliation = None
        self.phone_number = None
        self.leader_role = None
        self.rank = None
        self.department = None
        self.work_phone = None
        self.work_email = None
        self.role = None
        self.db = DBStaff()

    def register_staff(self, first_name, last_name, identification_form, email, affiliation, phone_number,
                       leader_role, rank, department, work_phone, work_email, pwd, identification_number):
        result = self.db.register_staff(first_name, last_name, identification_form, email, affiliation, phone_number,
                       leader_role, rank, department, work_phone, work_email, pwd, identification_number)
        if result != -1:
            self.first_name = first_name
            self.last_name = last_name
            self.identification_form = identification_form
            self.email = email
            self.affiliation = affiliation
            self.phone_number = phone_number
            self.leader_role = leader_role
            self.rank = rank
            self.department = department
            self.work_phone = work_phone
            self.work_email = work_email
        return result

    def retrieve_staff(self, first_name=None, last_name=None, identification_form=None, email=None, affiliation=None,
                         phone_number=None, leader_role=None, rank=None, department=None, work_phone=None, work_email=None, pwd=None):
        result = self.db.retrieve_staff(first_name=first_name, last_name=last_name, email=email, rank=rank, pwd=pwd,
                                          identification_form=identification_form, affiliation=affiliation,
                                          phone_number=phone_number, leader_role=leader_role, department=department,
                                          work_phone=work_phone, work_email=work_email)
        print(result)
        return result

    def modify_staff(self,first_name=None, last_name=None, identification_form=None, email=None, affiliation=None,
                         phone_number=None, leader_role=None, rank=None, department=None, work_phone=None, work_email=None,
                       pwd=None):
        result = self.db.modify_staff(id=self.identification_number,  first_name=first_name, last_name=last_name,
                                 rank=rank, identification_form=identification_form, affiliation=affiliation, email=email,
                                 phone_number=phone_number, leader_role=leader_role, department=department, pwd=pwd,
                                        work_phone=work_phone, work_email=work_email)
        if result:
            if first_name is not None:
                self.first_name = first_name
            if last_name is not None:
                self.last_name = last_name
            if identification_form is not None:
                self.identification_form = identification_form
            if email is not None:
                self.email = email
            if affiliation is not None:
                self.affiliation = affiliation
            if phone_number is not None:
                self.phone_number = phone_number
            if pwd is not None:
                self.pwd = pwd
            if rank is not None:
                self.rank = rank
            if leader_role is not None:
                self.leader_role = leader_role
            if department is not None:
                self.department = department
            if work_phone is not None:
                self.work_phone = work_phone
            if work_email is not None:
                self.work_email = work_email

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
        :param active: boolean, whether account is activated or not
        :return:
        """
        sql = "INSERT INTO users (first_name, last_name, email, phone_number, pwd, role, active)" \
              "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        is_register = False
        already_regist = self.retrieve_user(email=email)
        if len(already_regist) > 0:
            is_register = False
        else:
            # try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (str(first_name), str(last_name), str(email),
                                     str(phone_number), str(pwd), str(role), active))
            self.conn.commit()
            is_register = True
            # except:
            #     is_register = False

            if is_register:
                return self.retrieve_user(first_name=first_name, last_name=last_name, email=email, pwd=pwd, role=role)[0]["identification_number"]
            else:
                return -1

    def modify_user(self, id, first_name=None, last_name=None, email=None, phone_number=None, pwd=None):
        """
        To modify user information about input data
        :param id: int, user's id (identification number)
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param email: string, user's email
        :param phone_number: string, user's phone number
        :return:
        """
        sql = "UPDATE users SET "
        if first_name is not None:
            sql += "first_name='"+first_name+"', "
        if last_name is not None:
            sql += "last_name='"+last_name+"', "
        if email is not None:
            sql += "email='" + email + "', "
        if phone_number is not None:
            sql += "phone_number='" + phone_number + "', "
        if pwd is not None:
            sql += "pwd='"+pwd+"', "

        sql += "invitation_code=''"

        sql += " WHERE identification_number="+str(id)
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                self.conn.commit()
                return True
        except:
            return False

    def retrieve_user(self, id=None, first_name=None, last_name=None, email=None,
                      phone_number=None, pwd=None, role=None, invitation_code=None):
        """
        To retrieve users about input data
        :param id: int, user's id (identification number)
        :param first_name: string, user's first name
        :param last_name: string, user's last name
        :param email: string, user's email
        :param phone_number: string, user's phone number
        :return:
        """
        sql = "SELECT * FROM users"
        if any([first_name, last_name, email, phone_number, pwd, role, invitation_code]):  # if more than one inputs are not none, any() returns true
            sql += " WHERE "
        if id is not None:
            sql += "identification_number="+id
            if any([id, last_name, email, phone_number, pwd, role, invitation_code]):
                sql += " AND "
        if first_name is not None:
            sql += "first_name='"+first_name+"'"
            if any([last_name, email, phone_number, pwd, role, invitation_code]):
                sql += " AND "
        if last_name is not None:
            sql += "last_name='"+last_name+"'"
            if any([email, phone_number, pwd, role, invitation_code]):
                sql += " AND "
        if email is not None:
            sql += "email='" + email + "'"
            if any([phone_number, pwd, role, invitation_code]):
                sql += " AND "
        if phone_number is not None:
            sql += "phone_number='" + phone_number + "'"
            if any([pwd, role, invitation_code]):
                sql += " AND "
        if pwd is not None:
            sql += "pwd='" + pwd + "'"
            if any([role, invitation_code]):
                sql += " AND "
        if role is not None:
            sql += "role='" + role + "'"
            if any([invitation_code]):
                sql += " AND "
        if invitation_code is not None:
            sql += "invitation_code='" + invitation_code + "'"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        except:
            return []

    def delete_user(self, id):
        """
        To delet course
        :param id: int, user's id (identification number)
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


class DBPhysician(DBUser):
    """
    Class for evaluator
    it inherits User class
    """
    def __init__(self):
        super().__init__()

    def register_physician(self, first_name, last_name, identification_form, email, affiliation, phone_number,
                           qualification, evaluation_history, rank, department, work_phone, work_email, pwd, identification_number):
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
        super().register_user(identification_number, first_name, last_name, identification_form, email, affiliation, phone_number, pwd)
        sql = "INSERT INTO evaluator (identification_number, qualification, evaluation_history, cur_rank, department," \
              " work_phone, work_email) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        if identification_number == -1:
            return identification_number
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (identification_number, qualification, evaluation_history, rank, department, work_phone, work_email))
            self.conn.commit()
            return identification_number
        except:
            return identification_number

    def modify_physician(self, id, first_name=None, last_name=None, identification_form=None, email=None,
                         affiliation=None, phone_number=None, qualification=None, evaluation_history=None, rank=None,
                         department=None, work_phone=None, work_email=None, pwd=None):
        """
        To modify evaluator with user's information
        :param id: int, identification number
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
        super().modify_user(id, first_name, last_name, identification_form, email, affiliation, phone_number, pwd)
        sql = "UPDATE physician SET "
        if qualification is not None:
            sql += "qualification='" + qualification + "'"
            if any([evaluation_history, rank, department, work_phone, work_email]):
                sql += ", "
        if evaluation_history is not None:
            sql += "evaluation_history='" + evaluation_history + "'"
            if any([rank, department, work_phone, work_email]):
                sql += ", "
        if rank is not None:
            sql += "cur_rank='" + rank + "'"
            if any([department, work_phone, work_email]):
                sql += ", "
        if department is not None:
            sql += "department='" + department + "'"
            if any([work_phone, work_email]):
                sql += ", "
        if work_phone is not None:
            sql += "work_phone='" + work_phone + "'"
            if any([work_email]):
                sql += ", "
        if phone_number is not None:
            sql += "phone_number='" + phone_number + "'"
        sql += " WHERE identification_number=" + str(id)

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                self.conn.commit()
                return True
        except:
            return False

    def retrieve_physician(self, first_name=None, last_name=None, identification_form=None, email=None,
                           affiliation=None, phone_number=None, qualification=None, evaluation_history=None, rank=None,
                           department=None, work_phone=None, work_email=None, pwd=None):
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
        # Need to Join
        sql = "SELECT * FROM physician"
        try:
            sql = "SELECT u.first_name, u.last_name, u.identification_form, u.email, u.affiliation, u.phone_number," \
                  " u.identification_number, e.id, u.role" \
                  " FROM users as u INNER JOIN physician as e ON u.identification_number = e.identification_number"
            if any([first_name, last_name, identification_form, email, affiliation, phone_number, qualification, rank,
                    department, work_phone, work_email]):
                sql += " WHERE "

            if first_name is not None:
                sql += "u.first_name='" + first_name + "'"
                if any([last_name, identification_form, email, affiliation, phone_number, qualification, evaluation_history, rank,
                        department, work_phone, work_email, pwd]):
                    sql += " AND "

            if last_name is not None:
                sql += "u.last_name='" + last_name + "'"
                if any([identification_form, email, affiliation, phone_number, qualification, rank,
                        department, work_phone, work_email, pwd]):
                    sql += " AND "

            if identification_form is not None:
                sql += "u.identification_form='" + identification_form + "'"
                if any([email, affiliation, phone_number, qualification, evaluation_history, rank, department, work_phone, work_email, pwd]):
                    sql += " AND "

            if email is not None:
                sql += "u.email='" + email + "'"
                if any([affiliation, phone_number, qualification, evaluation_history, rank, department, work_phone, work_email, pwd]):
                    sql += " AND "

            if affiliation is not None:
                sql += "u.affiliation='" + affiliation + "'"
                if any([phone_number, qualification, evaluation_history, rank, department, work_phone, work_email, pwd]):
                    sql += " AND "

            if phone_number is not None:
                sql += "u.phone_number='" + phone_number + "'"
                if any([qualification, evaluation_history, rank, department, work_phone, work_email, pwd]):
                    sql += " AND "

            if qualification is not None:
                sql += "a.qualification='" + qualification + "'"
                if any([evaluation_history, rank, department, work_phone, work_email, pwd]):
                    sql += " AND "

            if evaluation_history is not None:
                sql += "a.evaluation_history='" + evaluation_history + "'"
                if any([rank, department, work_phone, work_email, pwd]):
                    sql += " AND "

            if rank is not None:
                sql += "a.cur_rank='" + rank + "'"
                if any([department, work_phone, work_email, pwd]):
                    sql += " AND "

            if department is not None:
                sql += "a.department='" + department + "'"
                if any([work_phone, work_email, pwd]):
                    sql += " AND "

            if work_phone is not None:
                sql += "a.work_phone='" + work_phone + "'"
                if any([work_email, pwd]):
                    sql += " AND "

            if work_email is not None:
                sql += "a.work_email='" + work_email + "'"
                if any([pwd]):
                    sql += " AND "
            if pwd is not None:
                sql += "u.pwd='"+pwd+"'"


            # try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
            return result
        except:
            return []

    def delete_physician(self, id):
        """
        To delete evaluator
        :param id: int, identification number
        """
        result = super().delete_user(id)
        if result:
            try:
                with self.conn.cursor() as cursor:
                    sql = "delete from physician where identification_number=%s"
                    cursor.execute(sql, id)
                    self.conn.commit()
                    return True
            except:
                return False
        else:
            return False


class DBPatient(DBUser):
    """
    Class for trainee
    it inherits User class
    """
    def __init__(self):
        super().__init__()

    def register_patient(self, first_name, last_name, identification_form, email, affiliation, phone_number,
                         qualification, rank, department, work_phone, work_email, pwd, identification_number):
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
        super().register_user(identification_number, first_name, last_name, identification_form, email, affiliation, phone_number, pwd)
        sql = "INSERT INTO patient (identification_number, qualification, cur_rank, department, work_phone, work_email)" \
              " VALUES (%s, %s, %s, %s, %s, %s)"
        if identification_number == -1:
            return identification_number
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (identification_number, qualification, rank, department, work_phone, work_email))
            self.conn.commit()
            return identification_number
        except:
            return -1

    def modify_patient(self, id, first_name=None, last_name=None, identification_form=None, email=None, affiliation=None,
                       phone_number=None, qualification=None, rank=None, department=None, work_phone=None, work_email=None,
                       pwd=None):
        """
        To modify a trainee following input information
        :param id: int, identification number
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
        super().modify_user(id, first_name, last_name, identification_form, email, affiliation, phone_number, pwd)
        sql = "UPDATE patient SET "
        if qualification is not None:
            sql += "qualification='" + qualification + "'"
            if any([rank, department, work_phone, work_email]):
                sql += ", "
        if rank is not None:
            sql += "cur_rank='" + rank + "'"
            if any([department, work_phone, work_email]):
                sql += ", "
        if department is not None:
            sql += "department='" + department + "'"
            if any([work_phone, work_email]):
                sql += ", "
        if work_phone is not None:
            sql += "work_phone='" + work_phone + "'"
            if any([work_email]):
                sql += ", "
        if phone_number is not None:
            sql += "phone_number='" + phone_number + "'"
        sql += " WHERE identification_number=" + str(id)

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                self.conn.commit()
                return True
        except:
            return False

    def retrieve_patient(self, first_name=None, last_name=None, identification_form=None, email=None, affiliation=None,
                         phone_number=None, qualification=None, rank=None, department=None, work_phone=None, work_email=None, pwd=None, part_trainee_list=None):
        """
        to retrieve trainee following input data
        :param id: int, identification number
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
        sql = "SELECT * FROM patient"
        try:
            sql = "SELECT u.first_name, u.last_name, u.identification_form, u.email, u.affiliation, u.phone_number," \
                  " u.identification_number, t.id, u.role" \
                  " FROM users as u INNER JOIN patient as t ON u.identification_number = t.identification_number"
            if any([first_name, last_name, identification_form, email, affiliation, phone_number, qualification, rank,
                    department, work_phone, work_email, part_trainee_list]):
                sql += " WHERE "

            if first_name is not None:
                sql += "u.first_name='" + first_name + "'"
                if any([last_name, identification_form, email, affiliation, phone_number, qualification, rank,
                        department, work_phone, work_email, pwd, part_trainee_list]):
                    sql += " AND "

            if last_name is not None:
                sql += "u.last_name='" + last_name + "'"
                if any([identification_form, email, affiliation, phone_number, qualification, rank,
                        department, work_phone, work_email, pwd, part_trainee_list]):
                    sql += " AND "

            if identification_form is not None:
                sql += "u.identification_form='" + identification_form + "'"
                if any([email, affiliation, phone_number, qualification, rank, department, work_phone, work_email, pwd, part_trainee_list]):
                    sql += " AND "

            if email is not None:
                sql += "u.email='" + email + "'"
                if any([affiliation, phone_number, qualification, rank, department, work_phone, work_email, pwd, part_trainee_list]):
                    sql += " AND "

            if affiliation is not None:
                sql += "u.affiliation='" + affiliation + "'"
                if any([phone_number, qualification, rank, department, work_phone, work_email, pwd, part_trainee_list]):
                    sql += " AND "

            if phone_number is not None:
                sql += "u.phone_number='" + phone_number + "'"
                if any([qualification, rank, department, work_phone, work_email, pwd, part_trainee_list]):
                    sql += " AND "

            if qualification is not None:
                sql += "t.qualification='" + qualification + "'"
                if any([rank, department, work_phone, work_email, pwd, part_trainee_list]):
                    sql += " AND "

            if rank is not None:
                sql += "t.cur_rank='" + rank + "'"
                if any([department, work_phone, work_email, pwd, part_trainee_list]):
                    sql += " AND "

            if department is not None:
                sql += "t.department='" + department + "'"
                if any([work_phone, work_email, pwd, part_trainee_list]):
                    sql += " AND "

            if work_phone is not None:
                sql += "t.work_phone='" + work_phone + "'"
                if any([work_email, pwd, part_trainee_list]):
                    sql += " AND "

            if work_email is not None:
                sql += "t.work_email='" + work_email + "'"
                if any([pwd, part_trainee_list]):
                    sql += " AND "

            if pwd is not None:
                sql += "u.pwd='" + pwd + "'"
                if any([part_trainee_list]):
                    sql += " AND "

            if part_trainee_list is not None:
                cond  = ""
                for p in range(len(part_trainee_list)):
                    cond += str(part_trainee_list[p])
                    if p < len(part_trainee_list)-1:
                        cond += ", "
                sql += "t.identification_number IN (" + cond + ")"
            # try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                print(sql, result)
            return result
        except:
            return []

    def delete_patient(self, id):
        """
        To delete evaluator
        :param id: int, identification number
        :return: boolean, state of deleting trainee
        """
        result = super().delete_user(id)
        if result:
            try:
                with self.conn.cursor() as cursor:
                    sql = "delete from patient where identification_number=%s"
                    cursor.execute(sql, id)
                    self.conn.commit()
                    return True
            except:
                return False
        else:
            return False


class DBStaff(DBUser):
    def __init__(self):
        super().__init__()

    def register_staff(self, first_name, last_name, identification_form, email, affiliation, phone_number,
                       leader_role, rank, department, work_phone, work_email, pwd, identification_number):
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
        super().modify_user(identification_number, first_name, last_name, identification_form, email, affiliation, phone_number, pwd)
        sql = "INSERT INTO staff (identification_number,leader_role, cur_rank, department, work_phone, work_email)" \
              " VALUES (%s, %s, %s, %s, %s, %s)"
        if identification_number == -1:
            return identification_number
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (identification_number, leader_role, rank, department, work_phone, work_email))
            self.conn.commit()
            return identification_number
        except:
            return identification_number

    def modify_staff(self, id, first_name=None, last_name=None, identification_form=None, email=None, affiliation=None, phone_number=None,
                       leader_role=None, rank=None, department=None, work_phone=None, work_email=None, pwd=None):
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
        super().modify_user(id, first_name, last_name, identification_form, email, affiliation, phone_number, pwd)
        sql = "UPDATE author SET "
        if leader_role is not None:
            sql += "leader_role='" + leader_role + "'"
            if any([rank, department, work_phone, work_email]):
                sql += ", "
        if rank is not None:
            sql += " cur_rank='" + rank + "'"
            if any([department, work_phone, work_email]):
                sql += ", "
        if department is not None:
            sql += "department='" + department + "'"
            if any([work_phone, work_email]):
                sql += ", "
        if work_phone is not None:
            sql += "work_phone='" + work_phone + "'"
            if any([work_email]):
                sql += ", "
        if phone_number is not None:
            sql += "phone_number='" + phone_number + "'"
        sql += " WHERE identification_number=" + str(id)

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                self.conn.commit()
                return True
        except:
            return False

    def retrieve_staff(self, first_name=None, last_name=None, identification_form=None, email=None, affiliation=None,
                      phone_number=None,leader_role=None, rank=None, department=None, work_phone=None, work_email=None, pwd=None):
        """
        To retrieve staff information
        :return:
        """
        sql = "SELECT * FROM staff"
        try:
            sql = "SELECT u.first_name, u.last_name, u.identification_form, u.email, u.affiliation, u.phone_number," \
                  " u.identification_number, s.department, s.cur_rank, s.work_phone, s.work_email, u.role" \
                  " FROM users as u INNER JOIN staff as s ON u.identification_number = s.identification_number"
            if any([first_name, last_name, identification_form, email, affiliation, phone_number,leader_role, rank,
                    department, work_phone, work_email, pwd]):
                sql += " WHERE "

            if first_name is not None:
                sql += "u.first_name='"+first_name+"'"
                if any([last_name, identification_form, email, affiliation, phone_number,leader_role, rank,
                    department, work_phone, work_email, pwd]):
                    sql+=" AND "

            if last_name is not None:
                sql += "u.last_name='" + last_name + "'"
                if any([identification_form, email, affiliation, phone_number, leader_role, rank,
                        department, work_phone, work_email, pwd]):
                    sql += " AND "

            if identification_form is not None:
                sql += "u.identification_form='" + identification_form + "'"
                if any([email, affiliation, phone_number, leader_role, rank, department, work_phone, work_email, pwd]):
                    sql += " AND "

            if email is not None:
                sql += "u.email='" + email + "'"
                if any([affiliation, phone_number, leader_role, rank, department, work_phone, work_email, pwd]):
                    sql += " AND "

            if affiliation is not None:
                sql += "u.affiliation='" + affiliation + "'"
                if any([phone_number, leader_role, rank, department, work_phone, work_email, pwd]):
                    sql += " AND "

            if phone_number is not None:
                sql += "u.phone_number='" + phone_number + "'"
                if any([leader_role, rank, department, work_phone, work_email, pwd]):
                    sql += " AND "

            if leader_role is not None:
                sql += "s.leader_role='" + leader_role + "'"
                if any([rank, department, work_phone, work_email, pwd]):
                    sql += " AND "

            if rank is not None:
                sql += "s.cur_rank='" + rank + "'"
                if any([department, work_phone, work_email, pwd]):
                    sql += " AND "

            if department is not None:
                sql += "s.department='" + department + "'"
                if any([work_phone, work_email, pwd]):
                    sql += " AND "

            if work_phone is not None:
                sql += "s.work_phone='" + work_phone + "'"
                if any([work_email, pwd]):
                    sql += " AND "

            if work_email is not None:
                sql += "s.work_email='" + work_email + "'"
                if any([pwd]):
                    sql += " AND "
            if pwd is not None:
                sql += "u.pwd='" + pwd + "'"

            # try:
            with self.conn.cursor() as cursor:
                print(sql)
                cursor.execute(sql)
                result = cursor.fetchall()
            return result
        except:
            return []

    def delete_staff(self, id):
        """
        To delete staff information
        :param id: identification number
        :return: boolean, state of deleting the user
        """
        result = super().delete_user(id)
        if result:
            try:
                with self.conn.cursor() as cursor:
                    sql = "delete from staff where identification_number=%s"
                    cursor.execute(sql, id)
                    self.conn.commit()
                    return True
            except:
                return False
        else:
            return False